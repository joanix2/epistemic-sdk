from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass(frozen=True)
class ExecutionContext:
    """Input bindings; record observation ids to avoid training/test leakage."""
    inputs: Mapping[str, Any] = field(default_factory=dict)
    observation_ids: tuple[str, ...] = ()
