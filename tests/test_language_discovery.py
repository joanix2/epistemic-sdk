"""Generalized language discovery: every boolean operator and fuzzy function."""
import unittest
from collections.abc import Mapping
from typing import Any

from epistemic_sdk import LanguageM2, Operator, Sort
from epistemic_sdk.algorithms.language_discovery import LanguageDiscovery
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


def _boolean_evaluate(term: Term, inputs: Mapping[str, Any]) -> Any:
    if isinstance(term, Variable):
        return inputs[term.name]
    if isinstance(term, Application):
        args = [_boolean_evaluate(argument, inputs) for argument in term.arguments]
        if term.operator == "not":
            return not args[0]
        if term.operator == "and":
            return args[0] and args[1]
        if term.operator == "or":
            return args[0] or args[1]
        raise KeyError(term.operator)
    raise TypeError(f"unexpected term {term!r}")


def _boolean_language() -> LanguageM2:
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


BOOLEAN_FUNCTIONS = {
    "and": lambda a, b: a and b,
    "or": lambda a, b: a or b,
    "xor": lambda a, b: a != b,
    "nand": lambda a, b: not (a and b),
    "nor": lambda a, b: not (a or b),
    "xnor": lambda a, b: a == b,
}

BOOL_INPUTS = [(False, False), (False, True), (True, False), (True, True)]


class BooleanTests(unittest.TestCase):
    def test_discovers_every_boolean_operator(self):
        discovery = LanguageDiscovery(
            _boolean_language(), ("A", "B"), _boolean_evaluate, (False, True)
        )
        for name, fn in BOOLEAN_FUNCTIONS.items():
            with self.subTest(operator=name):
                training = [
                    ({"A": a, "B": b}, fn(a, b)) for a, b in BOOL_INPUTS[:3]
                ]
                test_inputs = {"A": BOOL_INPUTS[3][0], "B": BOOL_INPUTS[3][1]}
                test_output = fn(*BOOL_INPUTS[3])
                result = discovery.discover(training, test_inputs, test_output)
                self.assertIsNotNone(result.program)
                assert result.program is not None
                self.assertEqual(
                    _boolean_evaluate(result.program, test_inputs), test_output
                )

    def test_constructs_language_for_complex_functions(self):
        discovery = LanguageDiscovery(
            _boolean_language(), ("A", "B"), _boolean_evaluate, (False, True)
        )
        for _name, fn in BOOLEAN_FUNCTIONS.items():
            training = [({"A": a, "B": b}, fn(a, b)) for a, b in BOOL_INPUTS[:3]]
            result = discovery.discover(
                training, {"A": BOOL_INPUTS[3][0], "B": BOOL_INPUTS[3][1]}, fn(*BOOL_INPUTS[3])
            )
            # primitive functions (and/or) keep 3 operators; complex ones are lifted.
            self.assertGreaterEqual(len(result.language.operators), 3)


def _fuzzy_evaluate(term: Term, inputs: Mapping[str, Any]) -> Any:
    if isinstance(term, Variable):
        return inputs[term.name]
    if isinstance(term, Application):
        args = [_fuzzy_evaluate(argument, inputs) for argument in term.arguments]
        if term.operator == "comp":
            return 1.0 - args[0]
        if term.operator == "min":
            return min(args[0], args[1])
        if term.operator == "max":
            return max(args[0], args[1])
        raise KeyError(term.operator)
    raise TypeError(f"unexpected term {term!r}")


def _fuzzy_language() -> LanguageM2:
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


FUZZY_DOMAIN = (0.0, 0.25, 0.5, 0.75, 1.0)


class FuzzyTests(unittest.TestCase):
    def test_discovers_fuzzy_functions(self):
        discovery = LanguageDiscovery(
            _fuzzy_language(), ("A", "B"), _fuzzy_evaluate, FUZZY_DOMAIN
        )
        cases = {
            "min": (
                lambda a, b: min(a, b),
                [
                    ({"A": 0.0, "B": 0.0}, 0.0),
                    ({"A": 0.25, "B": 0.75}, 0.25),
                    ({"A": 1.0, "B": 1.0}, 1.0),
                ],
                {"A": 0.75, "B": 0.25},
                0.25,
            ),
            "max": (
                lambda a, b: max(a, b),
                [
                    ({"A": 0.0, "B": 0.0}, 0.0),
                    ({"A": 0.25, "B": 0.75}, 0.75),
                    ({"A": 1.0, "B": 1.0}, 1.0),
                ],
                {"A": 0.75, "B": 0.25},
                0.75,
            ),
            "fxor": (
                lambda a, b: max(min(a, 1.0 - b), min(1.0 - a, b)),
                [
                    ({"A": 0.0, "B": 0.0}, 0.0),
                    ({"A": 0.25, "B": 0.75}, 0.75),
                    ({"A": 1.0, "B": 1.0}, 0.0),
                ],
                {"A": 0.75, "B": 0.25},
                0.75,
            ),
        }
        for name, (_fn, training, test_inputs, test_output) in cases.items():
            with self.subTest(function=name):
                result = discovery.discover(training, test_inputs, test_output)
                self.assertIsNotNone(result.program)
                assert result.program is not None
                self.assertEqual(_fuzzy_evaluate(result.program, test_inputs), test_output)


if __name__ == "__main__":
    unittest.main()
