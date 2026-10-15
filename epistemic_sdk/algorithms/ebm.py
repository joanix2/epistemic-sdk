"""EBM (prioritization): rank candidate programs by fitness then parsimony.

EBM does not invent programs; it *prioritizes* them. Each candidate is scored by
the number of training cases it satisfies, minus a small parsimony penalty
proportional to its size, so that among equally-fitting programs the smaller one
ranks first. ``infer`` enumerates a bounded set of candidates and returns the
top ``top_k``.
"""

from collections.abc import Sequence
from typing import Any

from epistemic_sdk.algorithms.synthesis import (
    Case,
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
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term


class EBMRankingEngine:
    """Rank candidate programs by (cases matched, then parsimony)."""

    def __init__(self, config: SynthesisConfig, *, top_k: int = 5, max_nodes: int = 5) -> None:
        self.config = config
        self.top_k = top_k
        self.max_nodes = max_nodes

    def infer(
        self,
        graph: BeliefGraph[Any],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> Sequence[Hypothesis]:
        cases = cases_from_graph(graph, self.config.case_extractor)
        terms = enumerate_terms(self.config.grammar, self.config.variables, self.max_nodes)
        programs = tuple(program_from_term(term, self.config) for term in terms)
        ranked = self.rank(programs, cases)
        supporting = tuple(belief.id for belief in graph.beliefs)
        return tuple(
            Hypothesis(
                id=f"H_ebm_{i}",
                program=program,
                supporting_belief_ids=supporting,
                inference_mode=InferenceMode.ABDUCTION,
            )
            for i, (program, _score) in enumerate(ranked[: self.top_k])
        )

    def rank(
        self, programs: Sequence[ProgramM1], cases: Sequence[Case]
    ) -> tuple[tuple[ProgramM1, float], ...]:
        scored: list[tuple[ProgramM1, float]] = []
        for program in programs:
            matches = sum(
                1
                for inputs, expected in cases
                if self.config.evaluate(program.entrypoint, inputs) == expected
            )
            score = float(matches) - 0.01 * self._node_count(program.entrypoint)
            scored.append((program, score))
        scored.sort(key=lambda pair: -pair[1])
        return tuple(scored)

    def _node_count(self, term: Term) -> int:
        if isinstance(term, Application):
            return 1 + sum(self._node_count(argument) for argument in term.arguments)
        return 1
