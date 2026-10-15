from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from epistemic_sdk.observations.observation import Observation

from .belief import Belief
from .relation import Relation

S = TypeVar("S")

@dataclass(frozen=True)
class BeliefGraph(Generic[S]):
    observations: tuple[Observation[Any], ...] = ()
    beliefs: tuple[Belief[S], ...] = ()
    relations: tuple[Relation, ...] = ()
    version: int = 0
