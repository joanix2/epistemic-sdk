"""Bounded, deterministic enumeration respecting an M2 signature.

No observational equivalence is used to delete candidates: agreement on the
training set is not a proof of equivalence on future experiments. Enumeration
is lazy at the requested result sort, but subterm tables still grow rapidly.
Only exact sorts are supported; subsort coercions require an explicit operator.
"""
from collections.abc import Iterator
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
) -> Iterator[Term]:
    """Yield well-sorted terms by node count, then declaration order."""
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
                    table[size, operator.result].append(term)
                    if operator.result == result_sort:
                        yield term
