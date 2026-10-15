"""Operator invention: lifting a sub-expression into a new operator."""
import unittest

from epistemic_sdk import Equation, LanguageM2, Operator, Sort
from epistemic_sdk.algorithms.operator_invention import OperatorInvention
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable

A = Variable("A", "Bool")
B = Variable("B", "Bool")

XOR_EXPR = Application(
    "or",
    (
        Application("and", (A, Application("not", (B,)))),
        Application("and", (Application("not", (A,)), B)),
    ),
)


def _reduced_boolean_language() -> LanguageM2:
    return LanguageM2(
        id="boolean",
        version="1.0.0",
        sorts=(Sort("Bool"),),
        operators=(
            Operator("not", ("Bool",), "Bool"),
            Operator("and", ("Bool", "Bool"), "Bool"),
            Operator("or", ("Bool", "Bool"), "Bool"),
        ),
    )


class Tests(unittest.TestCase):
    def test_lift_adds_operator_axiom_and_bumps_version(self):
        invention = OperatorInvention()
        new_language = invention.lift(XOR_EXPR, _reduced_boolean_language(), "xor")

        self.assertEqual(len(new_language.operators), 4)
        xor = next(op for op in new_language.operators if op.name == "xor")
        self.assertEqual(xor.arguments, ("Bool", "Bool"))
        self.assertEqual(xor.result, "Bool")
        self.assertTrue(any(axiom.id == "xor_def" for axiom in new_language.axioms))
        self.assertEqual(new_language.version, "2.0.0")

    def test_lifted_operator_defines_the_expression(self):
        invention = OperatorInvention()
        new_language = invention.lift(XOR_EXPR, _reduced_boolean_language(), "xor")
        axiom = next(a for a in new_language.axioms if a.id == "xor_def")
        assert isinstance(axiom.statement, Equation)
        self.assertEqual(axiom.statement.left, Application("xor", (A, B)))
        self.assertEqual(axiom.statement.right, XOR_EXPR)

    def test_lifted_language_provides_xor_as_primitive(self):
        invention = OperatorInvention()
        new_language = invention.lift(XOR_EXPR, _reduced_boolean_language(), "xor")
        grammar = {op.name: len(op.arguments) for op in new_language.operators}
        self.assertEqual(grammar["xor"], 2)
        self.assertEqual(grammar["and"], 2)


if __name__ == "__main__":
    unittest.main()
