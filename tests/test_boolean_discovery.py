"""Acceptance tests for the boolean operator discovery experiment (Experiment 001)."""
import unittest

from epistemic_sdk import (
    ExecutionContext,
    Hypothesis,
    KnowledgeBase,
    KnowledgeStatus,
    ProgramM1,
    RelationType,
    ValidationStatus,
)
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.execution.program_runner import ProgramRunner
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable
from examples.boolean_operator_discovery.belief_updater import BooleanBeliefUpdater
from examples.boolean_operator_discovery.boolean_language import (
    BOOLEAN_LANGUAGE,
    CANDIDATE_OPERATORS,
    SEMANTICS,
    build_program,
)
from examples.boolean_operator_discovery.engine import BooleanDiscoveryEngine
from examples.boolean_operator_discovery.inference import BooleanInferenceEngine
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER
from examples.boolean_operator_discovery.knowledge_reviser import BooleanKnowledgeReviser
from examples.boolean_operator_discovery.sensor import BooleanSensor
from examples.boolean_operator_discovery.transformation import NotNotElimination
from examples.boolean_operator_discovery.validator import BooleanValidator


def _build_engine() -> BooleanDiscoveryEngine:
    transformation = NotNotElimination()
    runner = ProgramRunner(executor=BOOLEAN_INTERPRETER, transformations=(transformation,))
    inference = BooleanInferenceEngine(runner)
    return BooleanDiscoveryEngine(
        belief_updater=BooleanBeliefUpdater(),
        inference=inference,
        runner=runner,
        validator=BooleanValidator(),
        reviser=BooleanKnowledgeReviser(),
    )


class Tests(unittest.TestCase):
    def test_language_declared(self):
        self.assertEqual(BOOLEAN_LANGUAGE.id, "boolean")
        self.assertEqual(len(BOOLEAN_LANGUAGE.operators), 7)
        self.assertTrue(any(axiom.id == "double_negation" for axiom in BOOLEAN_LANGUAGE.axioms))

    def test_six_operators_respect_truth_tables(self):
        cases = ((False, False), (False, True), (True, False), (True, True))
        expected = {
            "and": (False, False, False, True),
            "or": (False, True, True, True),
            "xor": (False, True, True, False),
            "nand": (True, True, True, False),
            "nor": (True, False, False, False),
            "xnor": (True, False, False, True),
        }
        for operator, outputs in expected.items():
            fn = SEMANTICS[operator]
            self.assertEqual(tuple(fn(a, b) for a, b in cases), outputs)
        self.assertFalse(SEMANTICS["not"](True))
        self.assertTrue(SEMANTICS["not"](False))

    def test_maltyped_term_rejected(self):
        bad_op = ProgramM1(
            language_id="boolean", language_version="1.0.0",
            entrypoint=Application("bogus", ()),
        )
        with self.assertRaises(KeyError):
            BOOLEAN_INTERPRETER.execute(bad_op, ExecutionContext())
        unbound = ProgramM1(
            language_id="boolean", language_version="1.0.0",
            entrypoint=Variable("A", "Bool"),
        )
        with self.assertRaises(KeyError):
            BOOLEAN_INTERPRETER.execute(unbound, ExecutionContext())

    def test_observations_preserve_provenance(self):
        sensor = BooleanSensor()
        training = sensor.observe()
        self.assertEqual(len(training), 3)
        for observation in training:
            self.assertEqual(observation.sensor_id, "blackbox")
            self.assertEqual(observation.metadata["source"], "training")
        test = sensor.validation_observation()
        self.assertEqual(test.id, "obs_test")
        self.assertEqual(test.metadata["source"], "validation")

    def test_graph_preserves_relations(self):
        updater = BooleanBeliefUpdater()
        graph = updater.update(BeliefGraph(), BooleanSensor().observe())
        self.assertEqual(len(graph.beliefs), 3)
        self.assertEqual(len(graph.relations), 3)
        self.assertEqual(graph.version, 1)
        for relation in graph.relations:
            self.assertEqual(relation.type, RelationType.SUPPORTS)

    def test_hypotheses_are_programs(self):
        transformation = NotNotElimination()
        runner = ProgramRunner(executor=BOOLEAN_INTERPRETER, transformations=(transformation,))
        inference = BooleanInferenceEngine(runner)
        graph = BooleanBeliefUpdater().update(BeliefGraph(), BooleanSensor().observe())
        hypotheses = inference.infer(graph, KnowledgeBase())
        self.assertTrue(hypotheses)
        for hypothesis in hypotheses:
            self.assertIsInstance(hypothesis.program, ProgramM1)
            self.assertEqual(hypothesis.program.language_id, "boolean")

    def test_transformation_preserves_semantics(self):
        transformation = NotNotElimination()
        for operator in CANDIDATE_OPERATORS:
            wrapped = build_program(operator)  # not(not(op(A, B)))
            normalized = transformation.transform(wrapped)
            for a in (False, True):
                for b in (False, True):
                    context = ExecutionContext({"A": a, "B": b})
                    self.assertEqual(
                        BOOLEAN_INTERPRETER.execute(wrapped, context),
                        BOOLEAN_INTERPRETER.execute(normalized, context),
                    )

    def test_executions_use_program_runner(self):
        transformation = NotNotElimination()
        runner = ProgramRunner(executor=BOOLEAN_INTERPRETER, transformations=(transformation,))
        hypothesis = Hypothesis(id="H_test", program=build_program("xor"))
        result = runner.run(hypothesis, ExecutionContext({"A": True, "B": False}))
        self.assertNotEqual(result.original_program.entrypoint, result.executed_program.entrypoint)
        self.assertTrue(result.output)
        self.assertEqual(result.program_transformations, ("not_not_elimination",))

    def test_incorrect_operator_refuted(self):
        sensor = BooleanSensor()
        result = _build_engine().run(sensor.observe(), sensor.validation_observation())
        refuted_ids = {refutation.hypothesis.id for refutation in result.trace.refutations}
        self.assertEqual(len(result.trace.refutations), 5)
        self.assertIn("H_and", refuted_ids)
        self.assertIn("H_or", refuted_ids)
        self.assertNotIn("H_xor", refuted_ids)
        self.assertEqual(len(result.trace.surviving), 1)

    def test_validation_not_used_by_inference(self):
        sensor = BooleanSensor()
        result = _build_engine().run(sensor.observe(), sensor.validation_observation())
        observation_ids = {observation.id for observation in result.beliefs.observations}
        self.assertNotIn("obs_test", observation_ids)
        self.assertEqual(observation_ids, {"obs_1", "obs_2", "obs_3"})
        for belief in result.beliefs.beliefs:
            self.assertNotIn("obs_test", belief.evidence_ids)

    def test_discovers_xor_and_predicts(self):
        sensor = BooleanSensor()
        result = _build_engine().run(sensor.observe(), sensor.validation_observation())
        assert result.selected is not None
        assert result.report is not None
        self.assertEqual(result.selected.id, "H_xor")
        self.assertTrue(result.prediction)
        self.assertEqual(result.report.status, ValidationStatus.CORROBORATED)

    def test_active_knowledge_has_evidence(self):
        sensor = BooleanSensor()
        result = _build_engine().run(sensor.observe(), sensor.validation_observation())
        self.assertEqual(len(result.knowledge.entries), 1)
        knowledge = result.knowledge.entries[0]
        self.assertEqual(knowledge.status, KnowledgeStatus.ACTIVE)
        self.assertEqual(knowledge.hypothesis_id, "H_xor")
        self.assertTrue(knowledge.execution_ids)
        self.assertTrue(knowledge.validation_report_ids)
        self.assertTrue(knowledge.dependency_ids)

    def test_deterministic(self):
        first = _build_engine()
        second = _build_engine()
        r1 = first.run(BooleanSensor().observe(), BooleanSensor().validation_observation())
        r2 = second.run(BooleanSensor().observe(), BooleanSensor().validation_observation())
        assert r1.selected is not None
        assert r2.selected is not None
        self.assertEqual(r1.prediction, r2.prediction)
        self.assertEqual(r1.selected.id, r2.selected.id)


if __name__ == "__main__":
    unittest.main()
