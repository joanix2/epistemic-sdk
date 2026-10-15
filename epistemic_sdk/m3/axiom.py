from dataclasses import dataclass
from typing import Literal
from .statement import Statement

@dataclass(frozen=True)
class Axiom:
    """Statement assumed in one theory, not a universally established truth."""
    id: str
    statement: Statement
    origin: Literal["definition", "assumption"]
