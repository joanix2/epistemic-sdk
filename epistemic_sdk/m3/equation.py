from __future__ import annotations
from dataclasses import dataclass
from .term import Term

@dataclass(frozen=True)
class Equation:
    """Logical equality; orienting it for reduction is a separate concern."""
    left: Term
    right: Term
