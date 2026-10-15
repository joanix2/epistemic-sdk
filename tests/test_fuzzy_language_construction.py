"""Fuzzy-logic exercise: the same four-point loop on a continuous domain.

Degrees are {0, 0.25, 0.5, 0.75, 1}; primitives are {min, max, comp}. The target
is the fuzzy XOR ``max(min(a, comp(b)), min(comp(a), b))``. The loop must
discover it, refute the wrong candidates on the independent case, construct the
language by inventing the ``fxor`` operator, and re-synthesize the short program.
"""
import unittest

from epistemic_sdk import Equation, LanguageM2, Operator, Sort
from epistemic_sdk.algorithms.operator_invention import OperatorInvention
from epistemic_sdk.algorithms.semantic_equivalence import SemanticEquivalence
from epistemic_sdk.algorithms.synthesis import enumerate_terms
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

A = Variable("A", "F")
B = Variable("B", "F")

FUZZY_DOMAIN = (0.0, 0.25, 0.5, 0.75, 1.0)
FUZZY_GRAMMAR = {"comp": 1, "min": 2, "max": 2}
VARIABLES = ("A", "B")

TRAINING = [
    ({"A": 0.0, "B": 0.0}, 0.0),
    ({"A": 0.25, "B": 0.75}, 0.75),
    ({"A": 1.0, "B": 1.0}, 0.0),
]
TEST_INPUT = {"A": 0.75, "B": 0.25}
TEST_OUTPUT = 0.75


def _evaluate(term, inputs):
    if isinstance(term, Variable):
        return inputs[term.name]
    if isinstance(term, Application):
        args = [_evaluate(argument, inputs) for argument in term.arguments]
        if term.operator == "min":
            return min(args[0], args[1])
        if term.operator == "max":
            return max(args[0], args[1])
        if term.operator == "comp":
            return 1.0 - args[0]
        raise KeyError(term.operator)
    raise TypeError(f"unexpected term {term!r}")


def _consistent_functions(training, max_nodes=9):
    equivalence = SemanticEquivalence(_evaluate, FUZZY_DOMAIN)
    representatives: list[Term] = []
    for term in enumerate_terms(FUZZY_GRAMMAR, VARIABLES, max_nodes):
        if not all(_evaluate(term, inputs) == output for inputs, output in training):
            continue
        if not any(equivalence.equivalent(rep, term) for rep in representatives):
            representatives.append(term)
    return representatives


def _base_language() -> LanguageM2:
    return LanguageM2(
        id="fuzzy",
        version="1.0.0",
        sorts=(Sort("F"),),
        operators=(
            Operator("comp", ("F",), "F"),
            Operator("min", ("F", "F"), "F"),
            Operator("max", ("F", "F"), "F"),
        ),
    )


class Tests(unittest.TestCase):
    def test_four_points_on_fuzzy_domain(self):
        functions = _consistent_functions(TRAINING)
        corroborated = [
            term for term in functions if _evaluate(term, TEST_INPUT) == TEST_OUTPUT
        ]
        refuted = [
            term for term in functions if _evaluate(term, TEST_INPUT) != TEST_OUTPUT
        ]
        self.assertTrue(corroborated)
        self.assertTrue(refuted)

        new_language = OperatorInvention().lift(corroborated[0], _base_language(), "fxor")
        self.assertEqual(len(new_language.operators), 4)
        self.assertEqual(new_language.version, "2.0.0")

        # The new operator is defined by its axiom: fxor(A, B) = <expression>.
        axiom = next(a for a in new_language.axioms if a.id == "fxor_def")
        assert isinstance(axiom.statement, Equation)
        self.assertEqual(_evaluate(axiom.statement.right, TEST_INPUT), TEST_OUTPUT)


if __name__ == "__main__":
    unittest.main()
