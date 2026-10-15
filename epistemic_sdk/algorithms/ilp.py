"""ILP (inductive logic programming) synthesis by bounded enumeration.

A minimal ILP-style abduction engine: enumerate every term over the grammar up
to ``max_nodes`` nodes, keep those consistent with every training case, and
deduplicate by semantic signature (the tuple of outputs across all cases) rather
than by syntax. Enumeration is complete *within the bound* but makes no claim
beyond it; cost grows combinatorially with ``max_nodes``.
"""

from collections.abc import Sequence
from typing import Any

from epistemic_sdk.algorithms.synthesis import (
    SynthesisConfig,
    cases_from_graph,
    enumerate_terms,
    program_from_term,
)
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.hypothesis import Hypothesis
from epistemic_sdk.m1.inference_mode import InferenceMode
from epistemic_sdk.m1.program_m1 import ProgramM1


class ILPAbductionEngine:
    """Abduce consistent programs by exhaustive bounded enumeration."""

    def __init__(
        self,
        config: SynthesisConfig,
        *,
        max_nodes: int = 5,
        max_results: int | None = None,
    ) -> None:
        self.config = config
        self.max_nodes = max_nodes
        self.max_results = max_results

    def infer(
        self,
        graph: BeliefGraph[Any],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> Sequence[Hypothesis]:
        cases = cases_from_graph(graph, self.config.case_extractor)
        expecteds = tuple(expected for _inputs, expected in cases)
        supporting = tuple(belief.id for belief in graph.beliefs)
        seen: set[tuple[Any, ...]] = set()
        hypotheses: list[Hypothesis] = []

        terms = enumerate_terms(self.config.grammar, self.config.variables, self.max_nodes)
        for term in terms:
            outputs = tuple(self.config.evaluate(term, inputs) for inputs, _e in cases)
            if outputs != expecteds:
                continue
            if outputs in seen:
                continue
            seen.add(outputs)
            hypotheses.append(
                Hypothesis(
                    id=f"H_ilp_{len(hypotheses)}",
                    program=program_from_term(term, self.config),
                    supporting_belief_ids=supporting,
                    inference_mode=InferenceMode.ABDUCTION,
                )
            )
            if self.max_results is not None and len(hypotheses) >= self.max_results:
                break
        return tuple(hypotheses)
