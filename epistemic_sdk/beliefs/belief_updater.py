from typing import Any, Protocol, Sequence, TypeVar
from epistemic_sdk.observations.observation import Observation
from .belief_graph import BeliefGraph

S = TypeVar("S")

class BeliefUpdater(Protocol[S]):
    """Revision of the belief graph given new observations."""
    def update(
        self,
        graph: BeliefGraph[S],
        observations: Sequence[Observation[Any]],
    ) -> BeliefGraph[S]:
        ...
