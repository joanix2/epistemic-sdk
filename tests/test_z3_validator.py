"""Tests for the Z3-based validator (optional dependency: z3-solver)."""
import unittest
from datetime import datetime, timezone

from epistemic_sdk import ExecutionContext, ExecutionResult, Observation, ProgramM1
from epistemic_sdk.algorithms.z3_validator import Z3Validator
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable
from epistemic_sdk.validation.validation_status import ValidationStatus


def _xor_program() -> ProgramM1:
    return ProgramM1(
        language_id="boolean",
        language_version="1.0.0",
        entrypoint=Application("xor", (Variable("A", "Bool"), Variable("B", "Bool"))),
    )


def _result(observation_ids: tuple[str, ...]) -> ExecutionResult[ProgramM1, bool]:
    program = _xor_program()
    return ExecutionResult(
        id="e1",
        hypothesis_id="H_xor",
        original_program=program,
        executed_program=program,
        raw_output=True,
        output=True,
        context=ExecutionContext({}, observation_ids=observation_ids),
    )


def _observation(id_: str, inputs: dict[str, bool], expected: bool) -> Observation:
    return Observation(id_, "sensor", (inputs, expected), datetime.now(timezone.utc))


def _extract(value: tuple[dict[str, bool], bool]) -> tuple[dict[str, bool], bool]:
    return value


class Tests(unittest.TestCase):
    def test_corroborated(self):
        validator = Z3Validator(_extract)
        observations = [
            _observation("o1", {"A": False, "B": False}, False),
            _observation("o2", {"A": False, "B": True}, True),
            _observation("o3", {"A": True, "B": False}, True),
            _observation("o4", {"A": True, "B": True}, False),
        ]
        report = validator.validate(_result(("o1", "o2", "o3", "o4")), observations)
        self.assertEqual(report.status, ValidationStatus.CORROBORATED)
        self.assertEqual(report.supporting_observation_ids, ("o1", "o2", "o3", "o4"))

    def test_refuted_with_counterexample(self):
        validator = Z3Validator(_extract)
        observations = [
            _observation("o1", {"A": False, "B": False}, False),
            _observation("o2", {"A": False, "B": False}, True),  # xor(F, F) is False
        ]
        report = validator.validate(_result(("o1", "o2")), observations)
        self.assertEqual(report.status, ValidationStatus.REFUTED)
        self.assertEqual(report.counterexample_ids, ("o2",))

    def test_inconclusive_without_observations(self):
        validator = Z3Validator(_extract)
        report = validator.validate(_result(()), [])
        self.assertEqual(report.status, ValidationStatus.INCONCLUSIVE)

    def test_symbolic_equivalence(self):
        validator = Z3Validator(_extract)
        a = Variable("A", "Bool")
        b = Variable("B", "Bool")
        xor = Application("xor", (a, b))
        xor_as_or_and = Application(
            "or",
            (
                Application("and", (a, Application("not", (b,)))),
                Application("and", (Application("not", (a,)), b)),
            ),
        )
        self.assertTrue(validator.equivalent(xor, xor_as_or_and))
        self.assertFalse(validator.equivalent(xor, Application("and", (a, b))))


if __name__ == "__main__":
    unittest.main()
