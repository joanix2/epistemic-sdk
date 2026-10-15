"""Concrete validators built on the validation contracts.

This package hosts replaceable :class:`Validator` implementations. They are kept
out of ``epistemic_sdk/validation/`` (which holds only the contracts) so that a
new algorithm never forces a change to the public protocol surface.
"""

from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import uuid4

from epistemic_sdk.execution.execution_result import ExecutionResult
from epistemic_sdk.observations.observation import Observation
from epistemic_sdk.validation.validation_report import ValidationReport
from epistemic_sdk.validation.validation_status import ValidationStatus

P = TypeVar("P")
R = TypeVar("R")


class ObservationValidator(Generic[P, R]):
    """Exact-match validation of an execution against independent observations.

    Compares the execution's *actual* output (``result.output``) against the
    *expected* value of each observation (``observation.value``) that is listed in
    ``result.context.observation_ids``. Only observations declared in that tuple
    are considered relevant; every other observation is ignored. This is what
    enforces the no-training/test-leakage invariant: an execution is only ever
    confronted with observations that were *not* used to produce its hypothesis.

    Rules:

    * No relevant observations -> :attr:`ValidationStatus.INCONCLUSIVE`, with no
      supporting ids and no counterexamples.
    * ``result.output`` equals every relevant observation's value ->
      :attr:`ValidationStatus.CORROBORATED`; ``supporting_observation_ids`` holds
      all relevant ids and ``counterexample_ids`` is empty.
    * Any relevant observation's value differs -> :attr:`ValidationStatus.REFUTED`;
      ``counterexample_ids`` holds the mismatching ids and
      ``supporting_observation_ids`` is empty.

    Limits (not proofs):

    * Equality is plain Python ``==`` between the observation's ``value`` (typed
      ``Any``, hence compared generically against ``R`` with no cast) and
      ``result.output``. Two values that are semantically equivalent but not
      ``==``-equal will be treated as mismatches.
    * This is exact-match validation on the declared domain of
      ``observation_ids``, not a universal claim. An absence of counterexamples
      corroborates only within the observed cases.
    * Independence of observations is *assumed*; it is guarded structurally by
      ``result.context.observation_ids``, but the validator cannot verify that a
      producer did not leak training data into those ids.
    """

    def __init__(self, validator_id: str = "observation_validator") -> None:
        self.validator_id = validator_id

    def validate(
        self,
        result: ExecutionResult[P, R],
        observations: Sequence[Observation[Any]],
    ) -> ValidationReport:
        relevant_ids = set(result.context.observation_ids)
        relevant = [obs for obs in observations if obs.id in relevant_ids]

        if not relevant:
            return self._report(
                result=result,
                status=ValidationStatus.INCONCLUSIVE,
                supporting_observation_ids=(),
                counterexample_ids=(),
            )

        counterexample_ids = tuple(
            obs.id for obs in relevant if obs.value != result.output
        )
        if counterexample_ids:
            status = ValidationStatus.REFUTED
            supporting_observation_ids: tuple[str, ...] = ()
        else:
            status = ValidationStatus.CORROBORATED
            supporting_observation_ids = tuple(obs.id for obs in relevant)

        return self._report(
            result=result,
            status=status,
            supporting_observation_ids=supporting_observation_ids,
            counterexample_ids=counterexample_ids,
        )

    def _report(
        self,
        *,
        result: ExecutionResult[P, R],
        status: ValidationStatus,
        supporting_observation_ids: tuple[str, ...],
        counterexample_ids: tuple[str, ...],
    ) -> ValidationReport:
        return ValidationReport(
            id=str(uuid4()),
            hypothesis_id=result.hypothesis_id,
            execution_id=result.id,
            status=status,
            supporting_observation_ids=supporting_observation_ids,
            counterexample_ids=counterexample_ids,
            validator_id=self.validator_id,
            timestamp=datetime.now(timezone.utc),
        )
