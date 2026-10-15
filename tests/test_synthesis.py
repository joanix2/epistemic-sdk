"""Tests for the Phase 2 synthesis engines (ILP, genetic, EBM, pipeline)."""
import unittest
from collections.abc import Mapping
from typing import Any

from epistemic_sdk.algorithms.ebm import EBMRankingEngine
from epistemic_sdk.algorithms.genetic import GeneticSynthesisEngine
from epistemic_sdk.algorithms.ilp import ILPAbductionEngine
from epistemic_sdk.algorithms.pipeline import PipelineInferenceEngine
from epistemic_sdk.algorithms.synthesis import SynthesisConfig
from epistemic_sdk.beliefs.belief import Belief
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

GRAMMAR = {"and": 2, "or": 2, "not": 1, "true": 0, "false": 0}
VARIABLES = ("A", "B")

AND_CASES = (
    ({"A": False, "B": False}, False),
    ({"A": False, "B": True}, False),
    ({"A": True, "B": False}, False),
    ({"A": True, "B": True}, True),
)


def _evaluate(term: Term, inputs: Mapping[str, Any]) -> Any:
    if isinstance(term, Variable):
        return inputs[term.name]
    if isinstance(term, Constant):
        return term.value
    if isinstance(term, Application):
        operator = term.operator
        arguments = [_evaluate(argument, inputs) for argument in term.arguments]
        if operator == "and":
            return arguments[0] and arguments[1]
        if operator == "or":
            return arguments[0] or arguments[1]
        if operator == "not":
            return not arguments[0]
        if operator == "true":
            return True
        if operator == "false":
            return False
        raise KeyError(f"unknown operator {operator}")
    raise TypeError(f"unexpected term {term!r}")


def _make_config() -> SynthesisConfig:
    return SynthesisConfig(
        grammar=GRAMMAR,
        variables=VARIABLES,
        evaluate=_evaluate,
        case_extractor=lambda proposition: proposition,
    )


def _make_graph(cases: tuple[tuple[dict[str, bool], bool], ...]) -> BeliefGraph[Any]:
    beliefs = tuple(
        Belief(id=f"b{i}", proposition=case, confidence=1.0, evidence_ids=())
        for i, case in enumerate(cases)
    )
    return BeliefGraph(beliefs=beliefs)


def _outputs(hypothesis: Any, cases: tuple[tuple[dict[str, bool], bool], ...]) -> tuple[Any, ...]:
    return tuple(_evaluate(hypothesis.program.entrypoint, inputs) for inputs, _ in cases)


def _expected(cases: tuple[tuple[dict[str, bool], bool], ...]) -> tuple[Any, ...]:
    return tuple(expected for _, expected in cases)


def _program(entrypoint: Term) -> ProgramM1:
    return ProgramM1(language_id="test", language_version="0", entrypoint=entrypoint)


class Tests(unittest.TestCase):
    def test_ilp_discovers_and_not_xor(self):
        engine = ILPAbductionEngine(_make_config(), max_nodes=3)
        hypotheses = list(engine.infer(_make_graph(AND_CASES), KnowledgeBase()))
        self.assertTrue(hypotheses)
        for hypothesis in hypotheses:
            self.assertEqual(_outputs(hypothesis, AND_CASES), _expected(AND_CASES))

    def test_ilp_max_results(self):
        engine = ILPAbductionEngine(_make_config(), max_nodes=3, max_results=3)
        hypotheses = list(engine.infer(_make_graph(AND_CASES), KnowledgeBase()))
        self.assertLessEqual(len(hypotheses), 3)

    def test_genetic_finds_consistent_program(self):
        engine = GeneticSynthesisEngine(
            _make_config(), population_size=100, generations=40, max_nodes=4, seed=0
        )
        hypotheses = list(engine.infer(_make_graph(AND_CASES), KnowledgeBase()))
        self.assertTrue(hypotheses)
        for hypothesis in hypotheses:
            self.assertEqual(_outputs(hypothesis, AND_CASES), _expected(AND_CASES))

    def test_ebm_ranks_consistent_above_inconsistent(self):
        config = _make_config()
        engine = EBMRankingEngine(config, top_k=5, max_nodes=3)
        a = Variable("A", "S")
        b = Variable("B", "S")
        and_program = _program(Application("and", (a, b)))
        or_program = _program(Application("or", (a, b)))
        ranked = engine.rank((or_program, and_program), AND_CASES)
        scores = {program: score for program, score in ranked}
        self.assertGreater(scores[and_program], scores[or_program])

    def test_pipeline_returns_consistent_program(self):
        config = _make_config()
        ilp = ILPAbductionEngine(config, max_nodes=3)
        genetic = GeneticSynthesisEngine(
            config, population_size=50, generations=20, max_nodes=4, seed=1
        )
        ebm = EBMRankingEngine(config, top_k=5, max_nodes=3)
        pipeline = PipelineInferenceEngine(ilp, genetic, ebm)
        hypotheses = list(pipeline.infer(_make_graph(AND_CASES), KnowledgeBase()))
        self.assertTrue(hypotheses)
        for hypothesis in hypotheses:
            self.assertEqual(_outputs(hypothesis, AND_CASES), _expected(AND_CASES))


if __name__ == "__main__":
    unittest.main()
