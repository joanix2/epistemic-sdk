"""Composition validation: the epistemic loop works with interchangeable inference engines.

Problem #2 (composition/architecture): make the SDK components work together
without artificial dependencies. The proof is that the SAME loop — sensor →
beliefs → inference → execution → validation — discovers XOR regardless of
which synthesis engine fills the inference slot. Each engine only sees the
``InferenceEngine`` protocol; none is coupled to the others.

This also exercises refutation (problem #3): the three training observations
are mathematically consistent with two distinct functions (XOR and
``and(B, not(A))``). The semantic dedup (by training signature) collapses them,
and enumeration returns the smallest consistent program — XOR — which the
held-out observation ``(True, False) → True`` then corroborates.
"""
import unittest
from collections.abc import Mapping
from typing import Any

from epistemic_sdk import (
    ExecutionContext,
    KnowledgeBase,
    ProgramM1,
    ProgramRunner,
    ValidationStatus,
)
from epistemic_sdk.algorithms.asp_synthesis import ASPSynthesisEngine
from epistemic_sdk.algorithms.ebm import EBMRankingEngine
from epistemic_sdk.algorithms.genetic import GeneticSynthesisEngine
from epistemic_sdk.algorithms.ilp import ILPAbductionEngine
from epistemic_sdk.algorithms.pipeline import PipelineInferenceEngine
from epistemic_sdk.algorithms.synthesis import SynthesisConfig
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.m3.term import Term
from examples.boolean_operator_discovery.belief_updater import BooleanBeliefUpdater
from examples.boolean_operator_discovery.boolean_language import BooleanSample
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER
from examples.boolean_operator_discovery.sensor import BooleanSensor
from examples.boolean_operator_discovery.validator import BooleanValidator

GRAMMAR = {"not": 1, "and": 2, "or": 2, "xor": 2, "nand": 2, "nor": 2, "xnor": 2}


def _evaluate(term: Term, inputs: Mapping[str, Any]) -> Any:
    program = ProgramM1(
        language_id="boolean", language_version="1.0.0", entrypoint=term
    )
    return BOOLEAN_INTERPRETER.execute(program, ExecutionContext(inputs))


def _extract(sample: BooleanSample) -> tuple[dict[str, bool], bool]:
    return ({"A": sample.a, "B": sample.b}, sample.output)


def _make_config() -> SynthesisConfig:
    return SynthesisConfig(
        grammar=GRAMMAR,
        variables=("A", "B"),
        evaluate=_evaluate,
        case_extractor=_extract,
        language_id="boolean",
        language_version="1.0.0",
    )


def _engines():
    config = _make_config()
    ilp = ILPAbductionEngine(config, max_nodes=3)
    asp = ASPSynthesisEngine(config, max_nodes=3)
    ebm = EBMRankingEngine(config, top_k=5, max_nodes=3)
    genetic = GeneticSynthesisEngine(
        config, population_size=200, generations=60, max_nodes=3, seed=0
    )
    pipeline = PipelineInferenceEngine(ilp, genetic, ebm)
    return [
        ("ilp", ilp),
        ("asp", asp),
        ("ebm", ebm),
        ("genetic", genetic),
        ("pipeline", pipeline),
    ]


def _run_loop(inference, training, test):
    graph = BooleanBeliefUpdater().update(BeliefGraph(), training)
    hypotheses = list(inference.infer(graph, KnowledgeBase()))
    sample = test.value
    runner = ProgramRunner(executor=BOOLEAN_INTERPRETER)
    validator = BooleanValidator()
    corroborated = []
    for hypothesis in hypotheses:
        result = runner.run(
            hypothesis,
            ExecutionContext({"A": sample.a, "B": sample.b}, observation_ids=(test.id,)),
        )
        report = validator.validate(result, (test,))
        if report.status == ValidationStatus.CORROBORATED:
            corroborated.append(hypothesis)
    return hypotheses, corroborated


class Tests(unittest.TestCase):
    def test_every_engine_discovers_xor(self):
        sensor = BooleanSensor()
        training = sensor.observe()
        test = sensor.validation_observation()
        for name, engine in _engines():
            with self.subTest(engine=name):
                hypotheses, corroborated = _run_loop(engine, training, test)
                self.assertTrue(corroborated, f"{name}: no corroborated hypothesis")
                predictions = [
                    BOOLEAN_INTERPRETER.execute(
                        hypothesis.program,
                        ExecutionContext({"A": True, "B": False}),
                    )
                    for hypothesis in corroborated
                ]
                self.assertIn(True, predictions, f"{name}: XOR not discovered")

    def test_semantic_dedup_returns_smallest_xor(self):
        # The 3 training cases admit two functions (XOR and and(B,not(A))); the
        # semantic dedup by training signature collapses them, and enumeration
        # returns the smallest consistent program: xor(A, B).
        engine = ILPAbductionEngine(_make_config(), max_nodes=3)
        sensor = BooleanSensor()
        hypotheses, corroborated = _run_loop(
            engine, sensor.observe(), sensor.validation_observation()
        )
        self.assertEqual(len(hypotheses), 1)
        self.assertEqual(len(corroborated), 1)


if __name__ == "__main__":
    unittest.main()
