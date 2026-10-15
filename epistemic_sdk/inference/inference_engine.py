from typing import Protocol, Sequence, TypeVar
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.hypothesis import Hypothesis
from epistemic_sdk.m1.program_m1 import ProgramM1

S = TypeVar("S")

class InferenceEngine(Protocol[S]):
    """Abduce/induce/deduce executable M1 hypotheses from a model."""
    def infer(
        self, graph: BeliefGraph[S], knowledge: KnowledgeBase[ProgramM1]
    ) -> Sequence[Hypothesis]:
        ...
