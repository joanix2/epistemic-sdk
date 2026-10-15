"""Shared contract for the Phase 2 synthesis engines (ILP, genetic, EBM).

A synthesis engine turns a finite set of training cases — variable bindings to
expected output — into candidate ``ProgramM1`` programs over a given grammar,
using an injected evaluator. The engines are domain-agnostic: they are
parameterised by a grammar, the input variable names, an evaluator, and a way to
extract cases from a belief graph. None of them uses a third-party dependency or
an LLM.

The evaluator is the same kind of finite semantics used by the Phase 1
``FiniteInterpreter``: a total, pure function over the declared domain.
"""

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from itertools import product
from typing import Any

from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

# One training case: variable bindings -> expected output.
Case = tuple[Mapping[str, Any], Any]

# A grammar maps an operator name to its arity (number of arguments).
Grammar = Mapping[str, int]

# Evaluate a (possibly substituted) term given variable bindings.
Evaluator = Callable[[Term, Mapping[str, Any]], Any]

# Extract a (inputs, expected_output) case from a belief proposition.
CaseExtractor = Callable[[Any], Case]

# Sort attached to generated variables. Synthesis is agnostic to sorts; the
# evaluator alone decides semantics, so a single placeholder sort is used.
_SORT = "S"


@dataclass(frozen=True)
class SynthesisConfig:
    """Everything a synthesis engine needs to know about its problem domain."""

    grammar: Grammar
    variables: tuple[str, ...]
    evaluate: Evaluator
    case_extractor: CaseExtractor
    language_id: str = "synthesis"
    language_version: str = "0.0.0"


def cases_from_graph(graph: Any, extractor: CaseExtractor) -> tuple[Case, ...]:
    """Extract the training cases from a belief graph's propositions."""
    return tuple(extractor(belief.proposition) for belief in graph.beliefs)


def program_from_term(term: Term, config: SynthesisConfig) -> ProgramM1:
    """Wrap a synthesized term into an M1 program of the configured language."""
    return ProgramM1(
        language_id=config.language_id,
        language_version=config.language_version,
        entrypoint=term,
    )


def _compositions(parts: int, total: int) -> Iterator[tuple[int, ...]]:
    """Yield every tuple of ``parts`` positive integers summing to ``total``."""
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - (parts - 1) + 1):
        for rest in _compositions(parts - 1, total - first):
            yield (first, *rest)


def enumerate_terms(
    grammar: Grammar, variables: tuple[str, ...], max_nodes: int
) -> tuple[Term, ...]:
    """Enumerate all terms over ``grammar`` with at most ``max_nodes`` nodes.

    Leaves are the input variables and nullary operators; internal nodes are
    operators applied to sub-terms whose sizes sum to ``size - 1``. The result is
    deterministic: increasing size, then structure. Cost grows combinatorially
    with ``max_nodes`` and the grammar's arities — it is meant for small spaces.
    """
    if max_nodes < 1:
        return ()

    memo: dict[int, tuple[Term, ...]] = {}

    def terms_of_size(size: int) -> tuple[Term, ...]:
        if size in memo:
            return memo[size]
        built: list[Term] = []
        if size == 1:
            built.extend(Variable(name, _SORT) for name in variables)
            built.extend(
                Application(name, ()) for name, arity in grammar.items() if arity == 0
            )
        else:
            for name, arity in grammar.items():
                if arity == 0:
                    continue
                for sizes in _compositions(arity, size - 1):
                    arg_options = [terms_of_size(s) for s in sizes]
                    built.extend(
                        Application(name, args) for args in product(*arg_options)
                    )
        memo[size] = tuple(built)
        return memo[size]

    output: list[Term] = []
    for size in range(1, max_nodes + 1):
        output.extend(terms_of_size(size))
    return tuple(output)
