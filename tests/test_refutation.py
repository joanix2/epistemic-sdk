"""Refutation/revision validation (problem #3).

A hypothesis that was corroborated and registered as active knowledge can be
refuted by a later observation, and the knowledge base is revised: the
``KnowledgeReviser`` turns the active entry into REFUTED while preserving its
provenance (hypothesis id, execution ids, validation report ids, dependencies).
This is the fallibilist core of the loop — knowledge is always revisable.
"""
import unittest
from datetime import datetime, timezone

from epistemic_sdk import (
    ExecutionContext,
    KnowledgeBase,
    KnowledgeStatus,
    Observation,
    ProgramRunner,
    ValidationStatus,
)
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from examples.boolean_operator_discovery.belief_updater import BooleanBeliefUpdater
from examples.boolean_operator_discovery.boolean_language import BooleanSample
from examples.boolean_operator_discovery.inference import BooleanInferenceEngine
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER
from examples.boolean_operator_discovery.knowledge_reviser import BooleanKnowledgeReviser
from examples.boolean_operator_discovery.sensor import BooleanSensor
from examples.boolean_operator_discovery.transformation import NotNotElimination
from examples.boolean_operator_discovery.validator import BooleanValidator


class Tests(unittest.TestCase):
    def test_new_observation_refutes_active_knowledge(self):
        belief_updater = BooleanBeliefUpdater()
        transformation = NotNotElimination()
        runner = ProgramRunner(executor=BOOLEAN_INTERPRETER, transformations=(transformation,))
        inference = BooleanInferenceEngine(runner)
        validator = BooleanValidator()
        reviser = BooleanKnowledgeReviser()

        sensor = BooleanSensor()
        training = sensor.observe()
        test = sensor.validation_observation()

        # Phase 1: discover XOR (only survivor of the 6 candidates) and corroborate it.
        graph = belief_updater.update(BeliefGraph(), training)
        hypotheses = list(inference.infer(graph, KnowledgeBase()))
        self.assertEqual(len(hypotheses), 1)
        xor = hypotheses[0]
        sample = test.value
        result = runner.run(
            xor,
            ExecutionContext({"A": sample.a, "B": sample.b}, observation_ids=(test.id,)),
        )
        report = validator.validate(result, (test,))
        self.assertEqual(report.status, ValidationStatus.CORROBORATED)
        base = reviser.revise(KnowledgeBase(), [xor], [report])
        self.assertEqual(base.entries[0].status, KnowledgeStatus.ACTIVE)

        # Phase 2: a NEW observation arrives that contradicts XOR: (True, False) -> False.
        new_observation = Observation(
            "obs_new",
            "sensor",
            BooleanSample(a=True, b=False, output=False),
            datetime.now(timezone.utc),
        )
        result2 = runner.run(
            xor,
            ExecutionContext({"A": True, "B": False}, observation_ids=("obs_new",)),
        )
        report2 = validator.validate(result2, (new_observation,))
        self.assertEqual(report2.status, ValidationStatus.REFUTED)
        self.assertEqual(report2.counterexample_ids, ("obs_new",))

        revised = reviser.revise(base, [xor], [report2])
        self.assertEqual(revised.entries[0].status, KnowledgeStatus.REFUTED)
        self.assertEqual(revised.entries[0].hypothesis_id, "H_xor")
        self.assertEqual(revised.entries[0].validation_report_ids, (report.id,))


if __name__ == "__main__":
    unittest.main()
