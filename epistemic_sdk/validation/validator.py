from collections.abc import Sequence
from typing import Any, Protocol, TypeVar

from epistemic_sdk.execution.execution_result import ExecutionResult
from epistemic_sdk.observations.observation import Observation

from .validation_report import ValidationReport

P = TypeVar("P")
R = TypeVar("R")

class Validator(Protocol[P, R]):
    """Compare execution predictions with actual independent observations.

    Invariant in ``P``/``R``: ``ExecutionResult`` is an invariant dataclass, so
    this port cannot be contravariant even though ``validate`` only consumes it.
    """
    def validate(
        self,
        result: ExecutionResult[P, R],
        observations: Sequence[Observation[Any]],
    ) -> ValidationReport:
        ...
