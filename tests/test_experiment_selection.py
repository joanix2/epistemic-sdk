"""Active experiment selection: a counter-example reconfigures what to seek next."""
import unittest

from epistemic_sdk import ExecutionContext, Hypothesis, ProgramM1
from epistemic_sdk.algorithms.disagreement_selector import DisagreementSelector
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER

A = Variable("A", "Bool")
B = Variable("B", "Bool")


def _program(entrypoint):
    return ProgramM1(language_id="boolean", language_version="1.0.0", entrypoint=entrypoint)


def _evaluate(program, inputs):
    return BOOLEAN_INTERPRETER.execute(program, ExecutionContext(inputs))


def _candidates():
    return [
        {"A": False, "B": False},
        {"A": False, "B": True},
        {"A": True, "B": False},
        {"A": True, "B": True},
    ]


class Tests(unittest.TestCase):
    def test_selector_picks_discriminating_experiment(self):
        xor = Hypothesis(id="H_xor", program=_program(Application("xor", (A, B))))
        not_a_and_b = Hypothesis(
            id="H_other",
            program=_program(Application("and", (Application("not", (A,)), B))),
        )
        selector = DisagreementSelector(_evaluate)
        chosen = selector.select([xor, not_a_and_b], _candidates())
        self.assertEqual(chosen, {"A": True, "B": False})

    def test_observation_refutes_the_wrong_hypothesis(self):
        xor = Hypothesis(id="H_xor", program=_program(Application("xor", (A, B))))
        not_a_and_b = Hypothesis(
            id="H_other",
            program=_program(Application("and", (Application("not", (A,)), B))),
        )
        chosen = {"A": True, "B": False}
        self.assertTrue(_evaluate(xor.program, chosen))
        self.assertFalse(_evaluate(not_a_and_b.program, chosen))


if __name__ == "__main__":
    unittest.main()
