"""Tests for the ASP (clingo) synthesis engine (optional dependency: clingo)."""
import importlib.util
import unittest
from collections.abc import Mapping
from typing import Any

from epistemic_sdk.algorithms.asp_synthesis import ASPSynthesisEngine
from epistemic_sdk.algorithms.synthesis import SynthesisConfig
from epistemic_sdk.beliefs.belief import Belief
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

_HAS_CLINGO = importlib.util.find_spec("clingo") is not None

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
        return bool(term.value)
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


def _make_graph(cases: tuple[tuple[dict[str, bool], bool], ...]) -> BeliefGraph:
    beliefs = tuple(
        Belief(id=f"b{i}", proposition=case, confidence=1.0, evidence_ids=())
        for i, case in enumerate(cases)
    )
    return BeliefGraph(beliefs=beliefs)


@unittest.skipUnless(_HAS_CLINGO, "clingo not installed")
class Tests(unittest.TestCase):
    def test_asp_discovers_and(self):
        engine = ASPSynthesisEngine(_make_config(), max_nodes=3)
        hypotheses = list(engine.infer(_make_graph(AND_CASES), KnowledgeBase()))
        self.assertTrue(hypotheses)
        for hypothesis in hypotheses:
            outputs = tuple(
                _evaluate(hypothesis.program.entrypoint, inputs) for inputs, _ in AND_CASES
            )
            self.assertEqual(outputs, tuple(expected for _, expected in AND_CASES))

    def test_asp_enumerates_same_space_as_ilp(self):
        engine = ASPSynthesisEngine(_make_config(), max_nodes=3)
        hypotheses = list(engine.infer(_make_graph(AND_CASES), KnowledgeBase()))
        self.assertTrue(any(hypothesis.id == "H_asp_0" for hypothesis in hypotheses))


if __name__ == "__main__":
    unittest.main()
