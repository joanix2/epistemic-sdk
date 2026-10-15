from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Mapping, TypeVar

V = TypeVar("V")

@dataclass(frozen=True)
class Observation(Generic[V]):
    """Recorded measurement. It may be wrong; provenance is essential."""
    id: str
    sensor_id: str
    value: V
    timestamp: datetime
    metadata: Mapping[str, Any] = field(default_factory=dict)
