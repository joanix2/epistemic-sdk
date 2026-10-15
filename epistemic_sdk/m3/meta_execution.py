from dataclasses import dataclass
from .term import Term

@dataclass(frozen=True)
class MetaExecution:
    """Bounded metalevel evaluation outcome (no claimed proof of termination)."""
    quoted_result: Term
    steps: int
    terminated: bool
