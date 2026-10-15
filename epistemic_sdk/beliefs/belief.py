from dataclasses import dataclass
from typing import Generic, TypeVar

S = TypeVar("S")

@dataclass(frozen=True)
class Belief(Generic[S]):
    """Interpreted statement supported by observations or beliefs.

    Confidence is optional; if provided, its calibration is model-specific.
    """
    id: str
    proposition: S
    confidence: float | None
    evidence_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...] = ()
