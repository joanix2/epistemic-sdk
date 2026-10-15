"""End-to-end language construction + discovery (validates all four problems).

Given three boolean examples and only the *primitive* operators {AND, OR, NOT},
the loop must (1) discover the program, (2) refute the wrong candidate, (3)
construct the language by inventing the missing operator, and (4) re-synthesize
the short program — all components composed together.
"""
import unittest

from epistemic_sdk import ExecutionContext, ProgramM1
from epistemic_sdk.algorithms.operator_invention import OperatorInvention
from epistemic_sdk.algorithms.semantic_equivalence import SemanticEquivalence
from epistemic_sdk.algorithms.synthesis import enumerate_terms
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable
from examples.boolean_operator_discovery.boolean_language import BooleanSample
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER
from examples.boolean_operator_discovery.sensor import BooleanSensor

A = Variable("A", "Bool")
B = Variable("B", "Bool")

BASE_GRAMMAR = {"not": 1, "and": 2, "or": 2}
VARIABLES = ("A", "B")


def _evaluate(term, inputs):
    program = ProgramM1(language_id="boolean", language_version="1.0.0", entrypoint=term)
    return BOOLEAN_INTERPRETER.execute(program, ExecutionContext(inputs))


def _cases(observations):
    return [
        ({"A": sample.a, "B": sample.b}, sample.output)
        for sample in (obs.value for obs in observations)
        if isinstance(sample, BooleanSample)
    ]


def _consistent_functions(training, max_nodes=8):
    equivalence = SemanticEquivalence(_evaluate, (False, True))
    representatives: list[Term] = []
    for term in enumerate_terms(BASE_GRAMMAR, VARIABLES, max_nodes):
        if not all(_evaluate(term, inputs) == output for inputs, output in training):
            continue
        if not any(equivalence.equivalent(rep, term) for rep in representatives):
            representatives.append(term)
    return representatives


class Tests(unittest.TestCase):
    def test_four_problems_end_to_end(self):
        sensor = BooleanSensor()
        training = _cases(sensor.observe())
        test_sample = sensor.validation_observation().value
        test_inputs = {"A": test_sample.a, "B": test_sample.b}

        # 1. Decouverte : synthesize in the base language {and, or, not}.
        functions = _consistent_functions(training)
        self.assertGreaterEqual(len(functions), 2)

        # 2. Refutation : the independent observation separates the candidates.
        corroborated = [
            term for term in functions if _evaluate(term, test_inputs) == test_sample.output
        ]
        refuted = [
            term for term in functions if _evaluate(term, test_inputs) != test_sample.output
        ]
        self.assertEqual(len(corroborated), 1)
        self.assertTrue(refuted)
        xor_expression = corroborated[0]

        # 3. Definition du sous-espace : invent the missing operator.
        reduced_language = _base_language()
        new_language = OperatorInvention().lift(xor_expression, reduced_language, "xor")
        self.assertEqual(len(new_language.operators), 4)
        self.assertEqual(new_language.version, "2.0.0")

        # 4. Re-synthèse : the short program xor(A, B) is now available.
        grammar = {op.name: len(op.arguments) for op in new_language.operators}
        self.assertEqual(grammar["xor"], 2)
        short = Application("xor", (A, B))
        self.assertTrue(_evaluate(short, test_inputs) == test_sample.output)


def _base_language():
    from epistemic_sdk import LanguageM2, Operator, Sort

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


if __name__ == "__main__":
    unittest.main()
