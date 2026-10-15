"""ASP synthesis: enumerate candidate programs using clingo (Answer Set Programming).

Optional dependency: ``clingo`` (declared in the ``asp`` extra), imported lazily
and dynamically. This engine encodes the grammar and a size bound as an ASP
program, lets clingo enumerate every candidate term up to that bound, then
evaluates each candidate against the training cases with the injected evaluator.
The *search* is the logic-programming part; the *semantics* remain the injected
evaluator (as in the other synthesis engines). Enumeration is complete within
the bound, but makes no claim beyond it.
"""

import importlib
from collections.abc import Sequence
from typing import Any

from epistemic_sdk.algorithms.synthesis import (
    SynthesisConfig,
    cases_from_graph,
    program_from_term,
)
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.hypothesis import Hypothesis
from epistemic_sdk.m1.inference_mode import InferenceMode
from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

_SORT = "S"


class ASPSynthesisEngine:
    """Abduce consistent programs by bounded enumeration via clingo."""

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
        self._clingo: Any = self._import_clingo()

    @staticmethod
    def _import_clingo() -> Any:
        try:
            return importlib.import_module("clingo")
        except ImportError as exc:
            raise ImportError(
                "ASPSynthesisEngine requires the optional dependency 'clingo' "
                "(install with: pip install clingo)"
            ) from exc

    def infer(
        self,
        graph: BeliefGraph[Any],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> Sequence[Hypothesis]:
        cases = cases_from_graph(graph, self.config.case_extractor)
        expected = tuple(output for _inputs, output in cases)
        supporting = tuple(belief.id for belief in graph.beliefs)
        seen: set[tuple[Any, ...]] = set()
        hypotheses: list[Hypothesis] = []

        for term in self._enumerate_terms():
            outputs = tuple(self.config.evaluate(term, inputs) for inputs, _e in cases)
            if outputs != expected or outputs in seen:
                continue
            seen.add(outputs)
            hypotheses.append(
                Hypothesis(
                    id=f"H_asp_{len(hypotheses)}",
                    program=program_from_term(term, self.config),
                    supporting_belief_ids=supporting,
                    inference_mode=InferenceMode.ABDUCTION,
                )
            )
            if self.max_results is not None and len(hypotheses) >= self.max_results:
                break
        return tuple(hypotheses)

    def _enumerate_terms(self) -> list[Term]:
        control = self._clingo.Control()
        control.configuration.solve.models = 0
        control.add("base", [], self._build_program())
        control.ground([("base", [])])
        terms: list[Term] = []
        control.solve(on_model=lambda model: terms.append(self._parse(model)))
        return terms

    def _build_program(self) -> str:
        lines: list[str] = []
        for name, arity in self.config.grammar.items():
            if arity == 0:
                lines.append(f'nullary("{name}").')
            else:
                lines.append(f'operator("{name}", {arity}).')
        for variable in self.config.variables:
            lines.append(f'variable("{variable}").')
        lines.append(f"node(1..{self.max_nodes}).")
        lines.append("used(1).")
        lines.append("used(M) :- child(_, _, M).")
        lines.append(
            "1 { label_var(N, V) : variable(V); "
            "label_const(N, C) : nullary(C); "
            "label_op(N, F) : operator(F, _) } 1 :- used(N)."
        )
        lines.append(
            "1 { child(N, P, M) : node(M), M > N } 1 "
            ":- label_op(N, F), operator(F, K), P = 1..K."
        )
        lines.append(":- child(N, _, _), not label_op(N, _).")
        return "\n".join(lines)

    def _parse(self, model: Any) -> Term:
        labels: dict[int, tuple[str, str]] = {}
        children: dict[tuple[int, int], int] = {}
        for atom in model.symbols(atoms=True):
            name = atom.name
            arguments = atom.arguments
            if name == "label_var":
                labels[arguments[0].number] = ("var", arguments[1].string)
            elif name == "label_const":
                labels[arguments[0].number] = ("const", arguments[1].string)
            elif name == "label_op":
                labels[arguments[0].number] = ("op", arguments[1].string)
            elif name == "child":
                children[(arguments[0].number, arguments[1].number)] = arguments[2].number
        return self._build(1, labels, children)

    def _build(
        self,
        node: int,
        labels: dict[int, tuple[str, str]],
        children: dict[tuple[int, int], int],
    ) -> Term:
        kind, name = labels[node]
        if kind == "var":
            return Variable(name, _SORT)
        if kind == "const":
            return Application(name, ())
        positions = sorted(pos for (parent, pos) in children if parent == node)
        arguments = tuple(
            self._build(children[(node, pos)], labels, children) for pos in positions
        )
        return Application(name, arguments)
