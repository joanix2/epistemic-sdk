"""Bounded, deterministic enumeration respecting an M2 signature.

By default no observational equivalence is used to delete candidates: agreement
on the training set is not a proof of equivalence on future experiments. A caller
may opt in with a ``signature`` of a term on its training inputs. Terms are then
visited by increasing size and a term with an already seen signature (or no
signature, i.e. undefined) is dropped. This keeps a smallest training-consistent
program, because a duplicate can always be replaced by its smaller twin, but it
hides the other training-consistent programs. Enumeration is lazy at the
requested result sort, but subterm tables still grow rapidly. Only exact sorts
are supported; subsort coercions require an explicit operator.
"""
from collections.abc import Callable, Hashable, Iterator
from dataclasses import dataclass
from itertools import product

from epistemic_sdk import Application, LanguageM2, Variable
from epistemic_sdk.m3.term import Term


class EnumerationLimit(Exception):
    """The finite allocation budget was reached before search exhaustion."""


@dataclass
class EnumerationBudget:
    limit: int
    generated: int = 0

    def consume(self) -> None:
        if self.generated >= self.limit:
            raise EnumerationLimit
        self.generated += 1


def _sizes(arity: int, total: int) -> Iterator[tuple[int, ...]]:
    if arity == 0:
        if total == 0:
            yield ()
    elif arity == 1:
        if total >= 1:
            yield (total,)
    else:
        for first in range(1, total - arity + 2):
            for rest in _sizes(arity - 1, total - first):
                yield (first, *rest)


def enumerate_typed_terms(
    language: LanguageM2,
    variables: tuple[Variable, ...],
    result_sort: str,
    max_nodes: int,
    budget: EnumerationBudget | None = None,
    signature: Callable[[Term], Hashable | None] | None = None,
) -> Iterator[Term]:
    """Yield well-sorted terms by node count, then declaration order.

    With ``signature``, keep only the first term per (sort, signature) and drop
    terms whose signature is ``None``; the caller must make an undefined
    subterm yield an undefined term for this pruning to be sound.
    """
    seen: set[tuple[str, Hashable]] = set()

    def keep(term: Term, sort: str) -> bool:
        if signature is None:
            return True
        key = signature(term)
        if key is None or (sort, key) in seen:
            return False
        seen.add((sort, key))
        return True

    sorts = {sort.name for sort in language.sorts}
    if result_sort not in sorts or any(v.sort not in sorts for v in variables):
        raise ValueError("undeclared variable or result sort")
    if len({op.name for op in language.operators}) != len(language.operators):
        raise ValueError("overloaded operator names are not supported")
    if any(
        op.result not in sorts or any(arg not in sorts for arg in op.arguments)
        for op in language.operators
    ):
        raise ValueError("operator uses an undeclared sort")

    relevant = {result_sort}
    while True:
        expanded = relevant | {arg for op in language.operators if op.result in relevant
                               for arg in op.arguments}
        if expanded == relevant:
            break
        relevant = expanded
    table: dict[tuple[int, str], list[Term]] = {}
    for size in range(1, max_nodes + 1):
        for sort in relevant:
            table[size, sort] = []
        if size == 1:
            for variable in variables:
                if variable.sort not in relevant:
                    continue
                if budget is not None:
                    budget.consume()
                if not keep(variable, variable.sort):
                    continue
                table[size, variable.sort].append(variable)
                if variable.sort == result_sort:
                    yield variable
        for operator in language.operators:
            if operator.result not in relevant:
                continue
            for sizes in _sizes(len(operator.arguments), size - 1):
                options = [
                    table.get((argument_size, sort), [])
                    for argument_size, sort in zip(sizes, operator.arguments, strict=True)
                ]
                for arguments in product(*options):
                    if budget is not None:
                        budget.consume()
                    term = Application(operator.name, arguments)
                    if not keep(term, operator.result):
                        continue
                    table[size, operator.result].append(term)
                    if operator.result == result_sort:
                        yield term
