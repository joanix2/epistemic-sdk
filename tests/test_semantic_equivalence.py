"""Semantic equivalence over a finite domain (exhaustive ground check)."""
import unittest

from epistemic_sdk import ExecutionContext, ProgramM1
from epistemic_sdk.algorithms.semantic_equivalence import SemanticEquivalence
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER

A = Variable("A", "Bool")
B = Variable("B", "Bool")


def _evaluate(term, inputs):
    program = ProgramM1(language_id="boolean", language_version="1.0.0", entrypoint=term)
    return BOOLEAN_INTERPRETER.execute(program, ExecutionContext(inputs))


def _xor_expr():
    return Application(
        "or",
        (
            Application("and", (A, Application("not", (B,)))),
            Application("and", (Application("not", (A,)), B)),
        ),
    )


class Tests(unittest.TestCase):
    def test_xor_equivalent_to_or_and(self):
        eq = SemanticEquivalence(_evaluate, (False, True))
        self.assertTrue(eq.equivalent(Application("xor", (A, B)), _xor_expr()))

    def test_xor_not_equivalent_to_and(self):
        eq = SemanticEquivalence(_evaluate, (False, True))
        self.assertFalse(eq.equivalent(Application("xor", (A, B)), Application("and", (A, B))))

    def test_commutativity(self):
        eq = SemanticEquivalence(_evaluate, (False, True))
        self.assertTrue(
            eq.equivalent(Application("and", (A, B)), Application("and", (B, A)))
        )


if __name__ == "__main__":
    unittest.main()
