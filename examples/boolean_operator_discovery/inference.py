"""Boolean inference engine: enumerate six candidates, eliminate the incompatible.

The search space is explicitly bounded to the six binary operators. Each
candidate is a genuine ``Hypothesis`` wrapping a ``ProgramM1``
(``not(not(op(A, B)))``), executed through the SDK's ``ProgramRunner`` on the
training cases taken from the belief graph. Candidates that disagree with any
training case are refuted (with an explicit counterexample); the rest survive.

The held-out validation observation is never consulted here: the engine only
reads ``graph.beliefs``, which are built exclusively from training observations.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from epistemic_sdk import ExecutionContext, Hypothesis, InferenceMode
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.execution.program_runner import ProgramRunner
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.program_m1 import ProgramM1

from .boolean_language import CANDIDATE_OPERATORS, BooleanSample, build_program


@dataclass(frozen=True)
class Refutation:
    """A candidate hypothesis and the first training case that refuted it."""

    hypothesis: Hypothesis
    counterexample: BooleanSample


@dataclass(frozen=True)
class InferenceTrace:
    """Result of candidate generation + elimination."""

    surviving: tuple[Hypothesis, ...]
    refutations: tuple[Refutation, ...]


class BooleanInferenceEngine:
    """Generate the six candidates and eliminate the incompatible ones."""

    def __init__(self, runner: ProgramRunner[bool]) -> None:
        self._runner = runner

    def infer(
        self,
        graph: BeliefGraph[BooleanSample],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> Sequence[Hypothesis]:
        return self.infer_with_trace(graph, knowledge).surviving

    def infer_with_trace(
        self,
        graph: BeliefGraph[BooleanSample],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> InferenceTrace:
        cases = tuple(belief.proposition for belief in graph.beliefs)
        surviving: list[Hypothesis] = []
        refutations: list[Refutation] = []

        for operator in CANDIDATE_OPERATORS:
            program = build_program(operator)
            hypothesis = Hypothesis(
                id=f"H_{operator}",
                program=program,
                inference_mode=InferenceMode.ABDUCTION,
            )
            counterexample = self._first_counterexample(hypothesis, cases)
            if counterexample is None:
                supporting = tuple(belief.id for belief in graph.beliefs)
                surviving.append(
                    Hypothesis(
                        id=hypothesis.id,
                        program=program,
                        supporting_belief_ids=supporting,
                        inference_mode=InferenceMode.ABDUCTION,
                    )
                )
            else:
                refutations.append(Refutation(hypothesis, counterexample))

        return InferenceTrace(surviving=tuple(surviving), refutations=tuple(refutations))

    def _first_counterexample(
        self, hypothesis: Hypothesis, cases: tuple[BooleanSample, ...]
    ) -> BooleanSample | None:
        for sample in cases:
            result = self._runner.run(
                hypothesis,
                ExecutionContext({"A": sample.a, "B": sample.b}),
            )
            if result.output != sample.output:
                return sample
        return None
