from dataclasses import dataclass
from typing import Generic, TypeVar

from .knowledge_status import KnowledgeStatus

P = TypeVar("P")

@dataclass(frozen=True)
class Knowledge(Generic[P]):
    """Revisable, corroborated program with auditable dependency links."""
    id: str
    program: P
    hypothesis_id: str
    execution_ids: tuple[str, ...]
    validation_report_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...]
    status: KnowledgeStatus
