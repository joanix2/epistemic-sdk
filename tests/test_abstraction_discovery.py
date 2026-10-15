"""Abstraction discovery: mining recurring fragments and scoring by compression."""
import unittest

from epistemic_sdk import LanguageM2, Operator, Sort
from epistemic_sdk.algorithms.abstraction_discovery import AbstractionDiscovery
from epistemic_sdk.algorithms.operator_invention import OperatorInvention
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable

A = Variable("A", "Bool")
B = Variable("B", "Bool")
C = Variable("C", "Bool")
D = Variable("D", "Bool")

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
    def test_mine_groups_by_alpha_equivalence(self):
        discovery = AbstractionDiscovery()
        corpus = [
            Application("and", (A, Application("not", (B,)))),
            Application("and", (C, Application("not", (D,)))),
        ]
        fragments = discovery.mine(corpus)
        by_pattern = {fragment.pattern: fragment for fragment in fragments}
        canonical = Application(
            "and",
            (Variable("x0", "Bool"), Application("not", (Variable("x1", "Bool"),))),
        )
        self.assertIn(canonical, by_pattern)
        self.assertEqual(by_pattern[canonical].occurrences, 2)

    def test_best_selects_most_compressible_fragment(self):
        discovery = AbstractionDiscovery()
        best = discovery.best([XOR_EXPR, XOR_EXPR, XOR_EXPR])
        self.assertIsNotNone(best)
        assert best is not None
        self.assertGreater(discovery.score(best), 0.0)
        self.assertEqual(best.occurrences, 3)

    def test_best_fragment_lifts_into_xor(self):
        discovery = AbstractionDiscovery()
        best = discovery.best([XOR_EXPR, XOR_EXPR, XOR_EXPR])
        assert best is not None
        new_language = OperatorInvention().lift(
            best.pattern, _reduced_boolean_language(), "xor"
        )
        self.assertTrue(any(op.name == "xor" for op in new_language.operators))
        self.assertEqual(new_language.version, "2.0.0")


if __name__ == "__main__":
    unittest.main()
