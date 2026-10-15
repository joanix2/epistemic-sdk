"""Semantic abstraction discovery: grouping fragments by function."""
import unittest

from epistemic_sdk import ExecutionContext, ProgramM1
from epistemic_sdk.algorithms.abstraction_discovery import AbstractionDiscovery
from epistemic_sdk.algorithms.semantic_abstraction_discovery import (
    SemanticAbstractionDiscovery,
)
from epistemic_sdk.algorithms.semantic_equivalence import SemanticEquivalence
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER

A = Variable("A", "Bool")
B = Variable("B", "Bool")


def _evaluate(term, inputs):
    program = ProgramM1(language_id="boolean", language_version="1.0.0", entrypoint=term)
    return BOOLEAN_INTERPRETER.execute(program, ExecutionContext(inputs))


def _xor_disjunction():
    return Application(
        "or",
        (
            Application("and", (A, Application("not", (B,)))),
            Application("and", (Application("not", (A,)), B)),
        ),
    )


def _xor_nand_form():
    return Application(
        "and",
        (
            Application("or", (A, B)),
            Application("not", (Application("and", (A, B)),)),
        ),
    )


class Tests(unittest.TestCase):
    def test_semantic_groups_equivalent_forms(self):
        equivalence = SemanticEquivalence(_evaluate, (False, True))
        semantic = SemanticAbstractionDiscovery(equivalence)
        syntactic = AbstractionDiscovery()
        corpus = [_xor_disjunction(), _xor_nand_form()]

        best = semantic.best(corpus)
        self.assertIsNotNone(best)
        assert best is not None
        self.assertEqual(best.occurrences, 2)
        self.assertGreater(semantic.score(best), 0.0)

        self.assertIsNone(syntactic.best(corpus))


if __name__ == "__main__":
    unittest.main()
