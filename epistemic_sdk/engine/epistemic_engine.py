from __future__ import annotations
from typing import Any, Protocol, Sequence, TypeVar
from epistemic_sdk.observations.observation import Observation
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.validation.validation_report import ValidationReport

S = TypeVar("S")

class EpistemicEngine(Protocol[S]):
    """One epistemic cycle: ingest -> infer -> execute -> validate -> revise."""
    def step(
        self, observations: Sequence[Observation[Any]]
    ) -> Sequence[ValidationReport]:
        ...

    @property
    def beliefs(self) -> BeliefGraph[S]:
        ...

    @property
    def knowledge(self) -> KnowledgeBase[ProgramM1]:
        ...
