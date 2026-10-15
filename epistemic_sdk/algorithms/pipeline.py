"""Pipeline: the mix ILP -> genetic -> EBM.

ILP proposes base programs, the genetic engine evolves/combines them, then EBM
prioritizes the union. This realizes the design "ILP proposes rules, the genetic
algorithm combines them, EBM prioritizes" as a single ``InferenceEngine``.
"""

from collections.abc import Sequence
from typing import Any

from epistemic_sdk.algorithms.ebm import EBMRankingEngine
from epistemic_sdk.algorithms.genetic import GeneticSynthesisEngine
from epistemic_sdk.algorithms.ilp import ILPAbductionEngine
from epistemic_sdk.algorithms.synthesis import cases_from_graph
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.hypothesis import Hypothesis
from epistemic_sdk.m1.inference_mode import InferenceMode
from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.m3.term import Term


class PipelineInferenceEngine:
    """Compose ILP (propose) -> genetic (combine) -> EBM (prioritize)."""

    def __init__(
        self,
        ilp: ILPAbductionEngine,
        genetic: GeneticSynthesisEngine,
        ebm: EBMRankingEngine,
    ) -> None:
        self.ilp = ilp
        self.genetic = genetic
        self.ebm = ebm

    def infer(
        self,
        graph: BeliefGraph[Any],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> Sequence[Hypothesis]:
        base = tuple(hypothesis.program for hypothesis in self.ilp.infer(graph, knowledge))
        evolved = self.genetic.evolve(graph, knowledge, seeds=base)
        candidates = self._deduplicate((*base, *evolved))
        cases = cases_from_graph(graph, self.ilp.config.case_extractor)
        ranked = self.ebm.rank(candidates, cases)
        supporting = tuple(belief.id for belief in graph.beliefs)
        return tuple(
            Hypothesis(
                id=f"H_mix_{i}",
                program=program,
                supporting_belief_ids=supporting,
                inference_mode=InferenceMode.ABDUCTION,
            )
            for i, (program, _score) in enumerate(ranked)
        )

    @staticmethod
    def _deduplicate(programs: Sequence[ProgramM1]) -> tuple[ProgramM1, ...]:
        seen: set[Term] = set()
        result: list[ProgramM1] = []
        for program in programs:
            if program.entrypoint not in seen:
                seen.add(program.entrypoint)
                result.append(program)
        return tuple(result)
