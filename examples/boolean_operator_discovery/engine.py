"""Boolean discovery engine: concrete orchestration of the epistemic loop.

Wires the boolean experiment's components into one engine implementing the
``EpistemicEngine`` shape (``step`` / ``beliefs`` / ``knowledge``), plus a
``run`` method that performs the full narrative: ingest training -> infer ->
eliminate -> select -> independent validation -> revise.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from epistemic_sdk import (
    ExecutionContext,
    Hypothesis,
    KnowledgeBase,
    Observation,
    ProgramM1,
    ValidationReport,
)
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.execution.program_runner import ProgramRunner

from .belief_updater import BooleanBeliefUpdater
from .boolean_language import BOOLEAN_LANGUAGE, CANDIDATE_OPERATORS, BooleanSample
from .inference import BooleanInferenceEngine, InferenceTrace
from .knowledge_reviser import BooleanKnowledgeReviser
from .validator import BooleanValidator


@dataclass(frozen=True)
class DiscoveryResult:
    """All intermediate steps of one discovery run, for the demo and the report."""

    language_id: str
    language_version: str
    training_observations: tuple[Observation[BooleanSample], ...]
    test_observation: Observation[BooleanSample]
    beliefs: BeliefGraph[BooleanSample]
    candidate_operators: tuple[str, ...]
    trace: InferenceTrace
    selected: Hypothesis | None
    prediction: bool | None
    report: ValidationReport | None
    knowledge: KnowledgeBase[ProgramM1]


class BooleanDiscoveryEngine:
    """Orchestrate the boolean operator discovery loop."""

    def __init__(
        self,
        *,
        belief_updater: BooleanBeliefUpdater,
        inference: BooleanInferenceEngine,
        runner: ProgramRunner[bool],
        validator: BooleanValidator,
        reviser: BooleanKnowledgeReviser,
    ) -> None:
        self._belief_updater = belief_updater
        self._inference = inference
        self._runner = runner
        self._validator = validator
        self._reviser = reviser
        self._beliefs: BeliefGraph[BooleanSample] = BeliefGraph()
        self._knowledge: KnowledgeBase[ProgramM1] = KnowledgeBase()

    @property
    def beliefs(self) -> BeliefGraph[BooleanSample]:
        return self._beliefs

    @property
    def knowledge(self) -> KnowledgeBase[ProgramM1]:
        return self._knowledge

    def step(self, observations: Sequence[Observation[Any]]) -> Sequence[ValidationReport]:
        """One cycle: ingest -> infer -> execute -> validate -> revise."""
        self._beliefs = self._belief_updater.update(self._beliefs, tuple(observations))
        hypotheses = self._inference.infer(self._beliefs, self._knowledge)
        reports: list[ValidationReport] = []
        for hypothesis in hypotheses:
            for observation in observations:
                sample = observation.value
                if not isinstance(sample, BooleanSample):
                    continue
                result = self._runner.run(
                    hypothesis,
                    ExecutionContext(
                        {"A": sample.a, "B": sample.b}, observation_ids=(observation.id,)
                    ),
                )
                reports.append(self._validator.validate(result, (observation,)))
        self._knowledge = self._reviser.revise(self._knowledge, list(hypotheses), reports)
        return reports

    def run(
        self,
        training: Sequence[Observation[BooleanSample]],
        test: Observation[BooleanSample],
    ) -> DiscoveryResult:
        """Run the full discovery narrative; the test observation is never inferred on."""
        self._beliefs = self._belief_updater.update(self._beliefs, tuple(training))
        trace = self._inference.infer_with_trace(self._beliefs, self._knowledge)

        selected = trace.surviving[0] if trace.surviving else None
        prediction: bool | None = None
        report: ValidationReport | None = None
        if selected is not None:
            sample = test.value
            result = self._runner.run(
                selected,
                ExecutionContext({"A": sample.a, "B": sample.b}, observation_ids=(test.id,)),
            )
            prediction = result.output
            report = self._validator.validate(result, (test,))
            self._knowledge = self._reviser.revise(self._knowledge, [selected], [report])

        return DiscoveryResult(
            language_id=BOOLEAN_LANGUAGE.id,
            language_version=BOOLEAN_LANGUAGE.version,
            training_observations=tuple(training),
            test_observation=test,
            beliefs=self._beliefs,
            candidate_operators=CANDIDATE_OPERATORS,
            trace=trace,
            selected=selected,
            prediction=prediction,
            report=report,
            knowledge=self._knowledge,
        )
