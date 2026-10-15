from collections.abc import Sequence
from typing import Protocol, TypeVar

from .observation import Observation

V = TypeVar("V")

class Sensor(Protocol[V]):
    """Transform the external environment into recorded observations.

    Invariant in ``V``: ``Observation`` is an invariant dataclass.
    """
    def observe(self) -> Sequence[Observation[V]]:
        ...
