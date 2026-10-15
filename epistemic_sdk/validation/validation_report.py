from dataclasses import dataclass
from datetime import datetime

from .validation_status import ValidationStatus


@dataclass(frozen=True)
class ValidationReport:
    """A claim about an execution, with explicit evidence provenance."""
    id: str
    hypothesis_id: str
    execution_id: str
    status: ValidationStatus
    supporting_observation_ids: tuple[str, ...]
    counterexample_ids: tuple[str, ...]
    validator_id: str
    timestamp: datetime
