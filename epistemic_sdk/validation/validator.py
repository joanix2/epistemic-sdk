from typing import Any, Protocol, Sequence, TypeVar
from epistemic_sdk.execution.execution_result import ExecutionResult
from epistemic_sdk.observations.observation import Observation
from .validation_report import ValidationReport

P = TypeVar("P", contravariant=True)
R = TypeVar("R", contravariant=True)

class Validator(Protocol[P, R]):
    """Compare execution predictions with actual independent observations."""
    def validate(
        self,
        result: ExecutionResult[P, R],
        observations: Sequence[Observation[Any]],
    ) -> ValidationReport:
        ...
