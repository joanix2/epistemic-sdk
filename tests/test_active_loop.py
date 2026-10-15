"""The active loop end to end: decide -> select -> observe -> update."""
import unittest

from epistemic_sdk import ExecutionContext, Hypothesis, ProgramM1
from epistemic_sdk.algorithms.active_loop import Action, ActiveController, ActiveLoop
from epistemic_sdk.algorithms.bayesian_updater import BayesianUpdater
from epistemic_sdk.algorithms.entropy_selector import EntropySelector
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable
from examples.boolean_operator_discovery.interpreter import BOOLEAN_INTERPRETER

A = Variable("A", "Bool")
B = Variable("B", "Bool")


def _program(entrypoint):
    return ProgramM1(language_id="boolean", language_version="1.0.0", entrypoint=entrypoint)


def _evaluate(program, inputs):
    return BOOLEAN_INTERPRETER.execute(program, ExecutionContext(inputs))


def _hypothesis(hypothesis_id, term):
    return Hypothesis(id=hypothesis_id, program=_program(term))


XOR_TERM = Application("xor", (A, B))
NOT_A_AND_B = Application("and", (Application("not", (A,)), B))
AND_TERM = Application("and", (A, B))

CANDIDATES = [
    {"A": False, "B": False},
    {"A": False, "B": True},
    {"A": True, "B": False},
    {"A": True, "B": True},
]


def _build_loop(observe):
    return ActiveLoop(
        controller=ActiveController(),
        selector=EntropySelector(_evaluate),
        updater=BayesianUpdater(_evaluate),
        observe=observe,
    )


class Tests(unittest.TestCase):
    def test_active_loop_identifies_xor(self):
        xor = _hypothesis("H_xor", XOR_TERM)
        other = _hypothesis("H_other", NOT_A_AND_B)
        loop = _build_loop(lambda inputs: _evaluate(_program(XOR_TERM), inputs))
        trace = loop.run([xor, other], CANDIDATES)

        first = trace.steps[0]
        self.assertEqual(first.action, Action.TESTER)
        self.assertEqual(first.experiment, {"A": True, "B": False})
        self.assertTrue(first.output)

        last = trace.steps[-1]
        self.assertEqual(last.action, Action.EXPLORER)
        self.assertAlmostEqual(last.distribution.probability("H_xor"), 1.0)
        self.assertAlmostEqual(last.distribution.probability("H_other"), 0.0)

    def test_active_loop_abduces_when_exhausted(self):
        wrong = _hypothesis("H_and", AND_TERM)
        loop = _build_loop(lambda inputs: _evaluate(_program(XOR_TERM), inputs))
        trace = loop.run([wrong], CANDIDATES)

        self.assertEqual(trace.steps[-1].action, Action.ABDURE)
        self.assertAlmostEqual(trace.steps[-1].distribution.probability("H_and"), 0.0)


if __name__ == "__main__":
    unittest.main()
