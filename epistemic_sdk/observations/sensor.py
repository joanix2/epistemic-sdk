from typing import Protocol, Sequence, TypeVar
from .observation import Observation

V = TypeVar("V", covariant=True)

class Sensor(Protocol[V]):
    """Transform the external environment into recorded observations."""
    def observe(self) -> Sequence[Observation[V]]:
        ...
