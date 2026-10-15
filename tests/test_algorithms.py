"""Tests for the Phase 1 algorithm implementations (stdlib only)."""
import unittest
from datetime import datetime, timezone

from epistemic_sdk import (
    Application,
    Constant,
    ExecutionContext,
    ExecutionResult,
    Observation,
    ProgramM1,
    ValidationStatus,
    Variable,
)
from epistemic_sdk.algorithms.enumeration_validator import ObservationValidator
from epistemic_sdk.algorithms.interpreter import FiniteInterpreter
from epistemic_sdk.algorithms.registry import AlgorithmRegistry
from epistemic_sdk.algorithms.rewriting import BoundedRewriter, matches, substitute
from examples.nat_language import EXAMPLE

NAT_SEMANTICS = {
    "zero": lambda: 0,
    "succ": lambda n: n + 1,
    "add": lambda a, b: a + b,
}


class Tests(unittest.TestCase):
    # --- rewriting ---
    def test_matches_variable_binding(self):
        x = Variable("X", "Nat")
        self.assertEqual(
            matches(x, Application("zero", ())),
            {"X": Application("zero", ())},
        )

    def test_matches_same_name_occurrence(self):
        x = Variable("X", "Nat")
        pattern = Application("add", (x, x))
        zero = Application("zero", ())
        succ_zero = Application("succ", (zero,))
        self.assertEqual(matches(pattern, Application("add", (zero, zero))), {"X": zero})
        self.assertIsNone(matches(pattern, Application("add", (zero, succ_zero))))

    def test_matches_constant_type_aware(self):
        self.assertEqual(matches(Constant(1, "Nat"), Constant(1, "Nat")), {})
        self.assertIsNone(matches(Constant(1, "Nat"), Constant(True, "Nat")))
        self.assertIsNone(matches(Constant(1, "Nat"), Constant(1, "Int")))

    def test_substitute(self):
        x = Variable("X", "Nat")
        zero = Application("zero", ())
        succ_zero = Application("succ", (zero,))
        result = substitute(Application("add", (x, zero)), {"X": succ_zero})
        self.assertEqual(result, Application("add", (succ_zero, zero)))

    def test_bounded_rewriter_transforms(self):
        rewriter = BoundedRewriter()
        out = rewriter.transform(EXAMPLE.program)
        self.assertEqual(out.entrypoint, Application("succ", (Application("zero", ()),)))
        self.assertEqual(out.language_id, "nat")
        self.assertEqual(out.candidate_rules, EXAMPLE.program.candidate_rules)
        self.assertEqual(rewriter.name, "bounded_rewriter")

    # --- interpreter ---
    def test_interpreter_evaluates(self):
        interp = FiniteInterpreter(NAT_SEMANTICS)
        self.assertEqual(interp.execute(EXAMPLE.program, ExecutionContext()), 1)

    def test_interpreter_variable_binding(self):
        interp = FiniteInterpreter(NAT_SEMANTICS)
        program = ProgramM1(
            language_id="nat", language_version="1.0.0",
            entrypoint=Variable("X", "Nat"),
        )
        self.assertEqual(interp.execute(program, ExecutionContext({"X": 3})), 3)

    def test_interpreter_constant(self):
        interp = FiniteInterpreter(NAT_SEMANTICS)
        program = ProgramM1(
            language_id="nat", language_version="1.0.0",
            entrypoint=Constant(42, "Nat"),
        )
        self.assertEqual(interp.execute(program, ExecutionContext()), 42)

    def test_interpreter_unbound_variable_raises(self):
        interp = FiniteInterpreter(NAT_SEMANTICS)
        program = ProgramM1(
            language_id="nat", language_version="1.0.0",
            entrypoint=Variable("X", "Nat"),
        )
        with self.assertRaises(KeyError):
            interp.execute(program, ExecutionContext())

    def test_interpreter_unknown_operator_raises(self):
        interp = FiniteInterpreter(NAT_SEMANTICS)
        program = ProgramM1(
            language_id="nat", language_version="1.0.0",
            entrypoint=Application("mul", (Application("zero", ()),)),
        )
        with self.assertRaises(KeyError):
            interp.execute(program, ExecutionContext())

    # --- validation ---
    def _result(self, output, observation_ids):
        return ExecutionResult(
            id="e1", hypothesis_id="H1",
            original_program=EXAMPLE.program, executed_program=EXAMPLE.program,
            raw_output=output, output=output,
            context=ExecutionContext({"x": 0}, observation_ids=observation_ids),
        )

    def test_validator_corroborated(self):
        validator = ObservationValidator()
        obs = Observation("o1", "sensor1", 1, datetime.now(timezone.utc))
        report = validator.validate(self._result(1, ("o1",)), [obs])
        self.assertEqual(report.status, ValidationStatus.CORROBORATED)
        self.assertEqual(report.supporting_observation_ids, ("o1",))
        self.assertEqual(report.counterexample_ids, ())

    def test_validator_refuted(self):
        validator = ObservationValidator()
        obs = Observation("o1", "sensor1", 99, datetime.now(timezone.utc))
        report = validator.validate(self._result(1, ("o1",)), [obs])
        self.assertEqual(report.status, ValidationStatus.REFUTED)
        self.assertEqual(report.counterexample_ids, ("o1",))
        self.assertEqual(report.supporting_observation_ids, ())

    def test_validator_inconclusive(self):
        validator = ObservationValidator()
        report = validator.validate(self._result(1, ()), [])
        self.assertEqual(report.status, ValidationStatus.INCONCLUSIVE)

    # --- registry ---
    def test_registry_register_and_pick(self):
        registry = AlgorithmRegistry()
        validator = ObservationValidator()
        registry.register("validation", "observation", validator)
        self.assertIs(registry.pick("validation", "observation"), validator)

    def test_registry_get_default(self):
        registry = AlgorithmRegistry()
        self.assertIsNone(registry.get("validation", "nope"))
        self.assertEqual(registry.get("validation", "nope", default="d"), "d")

    def test_registry_pick_missing_raises(self):
        registry = AlgorithmRegistry()
        with self.assertRaises(KeyError):
            registry.pick("validation", "nope")


if __name__ == "__main__":
    unittest.main()
