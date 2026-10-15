"""Semantic equivalence of terms over a finite domain (exhaustive ground check).

Two terms are equivalent when they produce the same output for every assignment
of their free variables over the domain. Exact for finite, deterministic
domains (the boolean case in particular): a decision procedure, not a
heuristic. This is what lets abstraction discovery recognize that ``xor(A, B)``
and ``or(and(A, not(B)), and(not(A), B))`` are the same function — beyond what
syntactic alpha-equivalence can see.
"""
from collections.abc import Callable, Mapping, Sequence
from itertools import product
from typing import Any

from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


class SemanticEquivalence:
    def __init__(
        self,
        evaluate: Callable[[Term, Mapping[str, Any]], Any],
        domain: Sequence[Any],
    ) -> None:
        self._evaluate = evaluate
        self._domain = tuple(domain)

    def equivalent(self, left: Term, right: Term) -> bool:
        variables = self._variables(left, right)
        names = tuple(variable.name for variable in variables)
        for assignment in product(self._domain, repeat=len(names)):
            inputs = dict(zip(names, assignment, strict=True))
            if self._evaluate(left, inputs) != self._evaluate(right, inputs):
                return False
        return True

    def _variables(self, *terms: Term) -> tuple[Variable, ...]:
        seen: list[Variable] = []

        def collect(node: Term) -> None:
            if isinstance(node, Variable):
                if not any(variable.name == node.name for variable in seen):
                    seen.append(node)
            elif isinstance(node, Application):
                for argument in node.arguments:
                    collect(argument)

        for term in terms:
            collect(term)
        return tuple(seen)
