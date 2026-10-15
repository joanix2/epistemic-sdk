"""Bayesian update of hypothesis probabilities (P(H | D)) and weighted selection."""
import unittest

from epistemic_sdk import ExecutionContext, Hypothesis, ProgramM1
from epistemic_sdk.algorithms.bayesian_updater import BayesianUpdater, HypothesisDistribution
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


def _xor():
    return Hypothesis(id="H_xor", program=_program(Application("xor", (A, B))))


def _not_a_and_b():
    return Hypothesis(
        id="H_other",
        program=_program(Application("and", (Application("not", (A,)), B))),
    )


class Tests(unittest.TestCase):
    def test_bayesian_update_refutes_incompatible(self):
        updater = BayesianUpdater(_evaluate)
        prior = HypothesisDistribution((("H_xor", 0.6), ("H_other", 0.4)))
        posterior = updater.update(
            [_xor(), _not_a_and_b()], prior, {"A": True, "B": False}, True
        )
        self.assertAlmostEqual(posterior.probability("H_xor"), 1.0)
        self.assertAlmostEqual(posterior.probability("H_other"), 0.0)

    def test_all_refuted_has_zero_mass(self):
        updater = BayesianUpdater(_evaluate)
        prior = HypothesisDistribution((("H_xor", 1.0),))
        posterior = updater.update([_xor()], prior, {"A": False, "B": False}, True)
        self.assertAlmostEqual(posterior.probability("H_xor"), 0.0)

    def test_entropy_selector_weights_by_probability(self):
        selector = EntropySelector(_evaluate)
        distribution = HypothesisDistribution((("H_xor", 0.9), ("H_other", 0.1)))
        candidates = [
            {"A": False, "B": False},
            {"A": False, "B": True},
            {"A": True, "B": False},
            {"A": True, "B": True},
        ]
        chosen = selector.select([_xor(), _not_a_and_b()], distribution, candidates)
        self.assertEqual(chosen, {"A": True, "B": False})


if __name__ == "__main__":
    unittest.main()
