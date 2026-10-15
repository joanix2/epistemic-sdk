"""Abstraction discovery (DreamCoder-style compression).

The missing piece of problem #4: WHICH fragment to lift. Given a corpus of
solved programs, enumerate their subterms, group them up to variable renaming
(alpha-equivalence), and score each fragment by its compression gain — the nodes
saved by lifting it into a primitive, minus the cost of its definition. This is
the minimum-description-length heuristic of DreamCoder's library learning: pure
subterm enumeration and counting, no LLM.
"""
from collections.abc import Sequence
from dataclasses import dataclass

from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


@dataclass(frozen=True)
class Fragment:
    """A liftable sub-expression: a canonicalized pattern and its statistics."""

    pattern: Term
    occurrences: int
    size: int
    arity: int


class AbstractionDiscovery:
    """Mine the corpus for recurring fragments and score them by compression."""

    def mine(self, corpus: Sequence[Term]) -> tuple[Fragment, ...]:
        counts: dict[Term, int] = {}
        for program in corpus:
            for subterm in self._subterms(program):
                canonical = self._canonical(subterm)
                if self._is_trivial(canonical):
                    continue
                counts[canonical] = counts.get(canonical, 0) + 1

        fragments = [
            Fragment(
                pattern=pattern,
                occurrences=occurrences,
                size=self._size(pattern),
                arity=self._arity(pattern),
            )
            for pattern, occurrences in counts.items()
        ]
        fragments.sort(key=lambda fragment: -self.score(fragment))
        return tuple(fragments)

    def score(self, fragment: Fragment) -> float:
        # Each occurrence shrinks from ``size`` nodes to ``1 + arity``; the
        # definition costs ``size`` nodes. Overlaps between fragments are
        # ignored: this is a heuristic proxy for the exact MDL gain.
        return float(
            fragment.occurrences * (fragment.size - 1 - fragment.arity) - fragment.size
        )

    def best(self, corpus: Sequence[Term]) -> Fragment | None:
        for fragment in self.mine(corpus):
            if self.score(fragment) > 0.0:
                return fragment
        return None

    def _subterms(self, term: Term) -> list[Term]:
        result: list[Term] = []

        def collect(node: Term) -> None:
            result.append(node)
            if isinstance(node, Application):
                for argument in node.arguments:
                    collect(argument)

        collect(term)
        return result

    def _canonical(self, term: Term) -> Term:
        mapping: dict[str, str] = {}

        def rename(node: Term) -> Term:
            if isinstance(node, Variable):
                if node.name not in mapping:
                    mapping[node.name] = f"x{len(mapping)}"
                return Variable(mapping[node.name], node.sort)
            if isinstance(node, Constant):
                return node
            if isinstance(node, Application):
                return Application(
                    node.operator, tuple(rename(argument) for argument in node.arguments)
                )
            raise TypeError(f"unexpected term {node!r}")

        return rename(term)

    def _is_trivial(self, term: Term) -> bool:
        if isinstance(term, Variable):
            return True
        if isinstance(term, Application):
            names = [
                argument.name for argument in term.arguments if isinstance(argument, Variable)
            ]
            if len(names) == len(term.arguments) and len(set(names)) == len(names):
                return True
        return False

    def _size(self, term: Term) -> int:
        if isinstance(term, (Variable, Constant)):
            return 1
        if isinstance(term, Application):
            return 1 + sum(self._size(argument) for argument in term.arguments)
        raise TypeError(f"unexpected term {term!r}")

    def _arity(self, term: Term) -> int:
        names: set[str] = set()

        def collect(node: Term) -> None:
            if isinstance(node, Variable):
                names.add(node.name)
            elif isinstance(node, Application):
                for argument in node.arguments:
                    collect(argument)

        collect(term)
        return len(names)
