from dataclasses import dataclass
from typing import Generic, TypeVar
from .knowledge import Knowledge

P = TypeVar("P")

@dataclass(frozen=True)
class KnowledgeBase(Generic[P]):
    entries: tuple[Knowledge[P], ...] = ()
    version: int = 0
