"""Abduction: mining a fragment and lifting it into a new operator."""
import unittest

from epistemic_sdk import LanguageM2, Operator, Sort
from epistemic_sdk.algorithms.abduction_operator import AbductionOperator
from epistemic_sdk.algorithms.abstraction_discovery import AbstractionDiscovery
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
    def test_abduce_lifts_best_fragment(self):
        operator = AbductionOperator(AbstractionDiscovery(), OperatorInvention())
        new_language = operator.abduce(
            [XOR_EXPR, XOR_EXPR, XOR_EXPR], _reduced_boolean_language(), "xor"
        )
        self.assertIsNotNone(new_language)
        assert new_language is not None
        self.assertTrue(any(op.name == "xor" for op in new_language.operators))
        self.assertEqual(new_language.version, "2.0.0")

    def test_abduce_returns_none_when_nothing_to_lift(self):
        operator = AbductionOperator(AbstractionDiscovery(), OperatorInvention())
        result = operator.abduce([XOR_EXPR], _reduced_boolean_language(), "xor")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
