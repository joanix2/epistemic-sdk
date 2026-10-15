"""Z3-based validator: encode a program term into Z3 and validate symbolically.

This adapter demonstrates the Phase 3 pattern for optional third-party
dependencies: the ``z3-solver`` package (declared in the ``z3`` extra) is
imported lazily and *dynamically* (``importlib.import_module``), so
``epistemic_sdk`` stays importable without it. Constructing
:class:`Z3Validator` raises a clear ``ImportError`` when ``z3-solver`` is absent.

Unlike the enumeration-based validators, this one re-encodes the program's
entrypoint term into a Z3 boolean expression and checks it *symbolically*
against each observation, and it can prove logical equivalence between two terms
(a capability exhaustive enumeration does not have, beyond a finite domain).
"""

import importlib
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from epistemic_sdk import (
    ExecutionResult,
    Observation,
    ProgramM1,
    ValidationReport,
    ValidationStatus,
)
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

# Extract (inputs, expected_output) from an observation's value.
CaseExtractor = Callable[[Any], tuple[Mapping[str, Any], Any]]


class Z3Validator:
    """Validate a boolean program term against observations using Z3."""

    def __init__(
        self, case_extractor: CaseExtractor, *, validator_id: str = "z3_validator"
    ) -> None:
        self.validator_id = validator_id
        self._case_extractor = case_extractor
        self._z3: Any = self._import_z3()

    @staticmethod
    def _import_z3() -> Any:
        try:
            return importlib.import_module("z3")
        except ImportError as exc:
            raise ImportError(
                "Z3Validator requires the optional dependency 'z3-solver' "
                "(install with: pip install 'epistemic-sdk[z3]')"
            ) from exc

    def validate(
        self,
        result: ExecutionResult[ProgramM1, bool],
        observations: Sequence[Observation[Any]],
    ) -> ValidationReport:
        expression = self._to_z3(result.executed_program.entrypoint)
        relevant_ids = set(result.context.observation_ids)
        relevant = [observation for observation in observations if observation.id in relevant_ids]
        if not relevant:
            return self._report(result, ValidationStatus.INCONCLUSIVE, (), ())

        supporting: list[str] = []
        counterexamples: list[str] = []
        for observation in relevant:
            inputs, expected = self._case_extractor(observation.value)
            if self._satisfies(expression, inputs, bool(expected)):
                supporting.append(observation.id)
            else:
                counterexamples.append(observation.id)

        if counterexamples:
            return self._report(result, ValidationStatus.REFUTED, (), tuple(counterexamples))
        return self._report(result, ValidationStatus.CORROBORATED, tuple(supporting), ())

    def equivalent(self, left: Term, right: Term) -> bool:
        """Return True when ``left`` and ``right`` are logically equivalent.

        Uses Z3 to check that ``Not(left == right)`` is unsatisfiable — a
        symbolic proof, not a finite-domain enumeration.
        """
        solver = self._z3.Solver()
        solver.add(self._z3.Not(self._to_z3(left) == self._to_z3(right)))
        return solver.check() == self._z3.unsat

    def _satisfies(self, expression: Any, inputs: Mapping[str, Any], expected: bool) -> bool:
        substitutions = [
            (self._z3.Bool(name), self._z3.BoolVal(bool(value)))
            for name, value in inputs.items()
        ]
        evaluated = self._z3.simplify(self._z3.substitute(expression, substitutions))
        return self._z3.is_true(evaluated) == expected

    def _to_z3(self, term: Term) -> Any:
        if isinstance(term, Variable):
            return self._z3.Bool(term.name)
        if isinstance(term, Constant):
            return self._z3.BoolVal(bool(term.value))
        if isinstance(term, Application):
            arguments = [self._to_z3(argument) for argument in term.arguments]
            return self._apply(term.operator, arguments)
        raise TypeError(f"unexpected term {term!r}")

    def _apply(self, operator: str, arguments: list[Any]) -> Any:
        z3 = self._z3
        if operator == "not":
            return z3.Not(arguments[0])
        if operator == "and":
            return z3.And(*arguments)
        if operator == "or":
            return z3.Or(*arguments)
        if operator == "xor":
            return z3.Xor(arguments[0], arguments[1])
        if operator == "nand":
            return z3.Not(z3.And(*arguments))
        if operator == "nor":
            return z3.Not(z3.Or(*arguments))
        if operator == "xnor":
            return z3.Not(z3.Xor(arguments[0], arguments[1]))
        raise ValueError(f"unsupported boolean operator: {operator}")

    def _report(
        self,
        result: ExecutionResult[ProgramM1, bool],
        status: ValidationStatus,
        supporting: tuple[str, ...],
        counterexamples: tuple[str, ...],
    ) -> ValidationReport:
        return ValidationReport(
            id=str(uuid4()),
            hypothesis_id=result.hypothesis_id,
            execution_id=result.id,
            status=status,
            supporting_observation_ids=supporting,
            counterexample_ids=counterexamples,
            validator_id=self.validator_id,
            timestamp=datetime.now(timezone.utc),
        )
