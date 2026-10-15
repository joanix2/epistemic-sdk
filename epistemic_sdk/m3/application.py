from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .term import Term

@dataclass(frozen=True)
class Application:
    operator: str
    arguments: tuple[Term, ...]
