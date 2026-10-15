"""Equality graph: saturation, congruence, and extraction."""
import unittest

from epistemic_sdk.algorithms.egraph import EGraph
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

A = Variable("A", "Bool")
B = Variable("B", "Bool")
X = Variable("X", "Bool")

F = Constant(False, "Bool")
T = Constant(True, "Bool")


def _not(term: Term) -> Application:
    return Application("not", (term,))


def _double_negation_rule() -> tuple[Term, Term]:
    return (_not(_not(X)), X)


class Tests(unittest.TestCase):
    def test_double_negation_saturation_and_extraction(self):
        egraph = EGraph()
        xor_class = egraph.add(Application("xor", (A, B)))
        double_neg = egraph.add(_not(_not(Application("xor", (A, B)))))
        egraph.saturate([_double_negation_rule()])

        self.assertEqual(egraph.find(double_neg), egraph.find(xor_class))
        self.assertEqual(egraph.extract(double_neg), Application("xor", (A, B)))

    def test_congruence_applies_in_subterms(self):
        egraph = EGraph()
        term = egraph.add(Application("and", (_not(_not(A)), B)))
        expected = egraph.add(Application("and", (A, B)))
        egraph.saturate([_double_negation_rule()])

        self.assertEqual(egraph.find(term), egraph.find(expected))
        self.assertEqual(egraph.extract(term), Application("and", (A, B)))

    def test_ground_truth_table_reduction(self):
        egraph = EGraph()
        term = egraph.add(
            Application(
                "or",
                (
                    Application("and", (F, _not(T))),
                    Application("and", (_not(F), T)),
                ),
            )
        )
        true_class = egraph.add(T)
        rules: list[tuple[Term, Term]] = [
            (_not(T), F),
            (_not(F), T),
            (Application("and", (F, F)), F),
            (Application("and", (T, T)), T),
            (Application("or", (F, T)), T),
        ]
        egraph.saturate(rules)

        self.assertEqual(egraph.find(term), egraph.find(true_class))
        self.assertEqual(egraph.extract(term), T)


if __name__ == "__main__":
    unittest.main()
