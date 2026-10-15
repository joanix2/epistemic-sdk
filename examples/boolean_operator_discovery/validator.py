"""Boolean validator: confront an execution's boolean output with observations.

The Phase 1 ``ObservationValidator`` performs exact ``==`` on the whole
observation value; here the observation value is a structured ``BooleanSample``
carrying inputs *and* output, so this validator extracts ``sample.output``
before the comparison. It enforces the same no-leakage guard: only observations
declared in ``result.context.observation_ids`` are considered, which is what
keeps the held-out validation observation out of the training fit-check.
"""

from collections.abc import Sequence
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

from .boolean_language import BooleanSample


class BooleanValidator:
    """Exact-match validation of a boolean execution against observations."""

    def __init__(self, validator_id: str = "boolean_validator") -> None:
        self.validator_id = validator_id

    def validate(
        self,
        result: ExecutionResult[ProgramM1, bool],
        observations: Sequence[Observation[Any]],
    ) -> ValidationReport:
        relevant_ids = set(result.context.observation_ids)
        relevant = [obs for obs in observations if obs.id in relevant_ids]

        if not relevant:
            return self._report(result, ValidationStatus.INCONCLUSIVE, (), ())

        supporting: list[str] = []
        counterexamples: list[str] = []
        for observation in relevant:
            sample = observation.value
            if isinstance(sample, BooleanSample) and sample.output == result.output:
                supporting.append(observation.id)
            else:
                counterexamples.append(observation.id)

        if counterexamples:
            status = ValidationStatus.REFUTED
            supporting = []
        else:
            status = ValidationStatus.CORROBORATED
        return self._report(result, status, tuple(supporting), tuple(counterexamples))

    def _report(
        self,
        result: ExecutionResult[ProgramM1, bool],
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
