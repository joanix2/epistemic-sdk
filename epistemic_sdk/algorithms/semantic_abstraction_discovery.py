"""Semantic abstraction discovery: group fragments by function, not syntax.

Extends :class:`AbstractionDiscovery` so that two syntactically different but
semantically equal sub-expressions — e.g. ``or(and(A, not(B)), and(not(A), B))``
and ``and(or(A, B), not(and(A, B)))``, both computing XOR — are counted as the
*same* fragment. This is the e-graph's "see equivalent patterns" idea, realised
here by exhaustive ground equivalence over a finite domain.
"""
from collections.abc import Sequence
from typing import Any

from epistemic_sdk.m3.term import Term

from .abstraction_discovery import AbstractionDiscovery, Fragment
from .semantic_equivalence import SemanticEquivalence


class SemanticAbstractionDiscovery(AbstractionDiscovery):
    """Group fragments by semantic equivalence (function) rather than syntax."""

    def __init__(self, equivalence: SemanticEquivalence) -> None:
        super().__init__()
        self._equivalence = equivalence

    def mine(self, corpus: Sequence[Term]) -> tuple[Fragment, ...]:
        groups: list[list[Any]] = []
        for program in corpus:
            for subterm in self._subterms(program):
                if self._is_trivial(subterm):
                    continue
                for group in groups:
                    if self._equivalence.equivalent(group[0], subterm):
                        group[1] += 1
                        break
                else:
                    groups.append([subterm, 1])

        fragments = [
            Fragment(
                pattern=representative,
                occurrences=occurrences,
                size=self._size(representative),
                arity=self._arity(representative),
            )
            for representative, occurrences in groups
        ]
        fragments.sort(key=lambda fragment: -self.score(fragment))
        return tuple(fragments)
