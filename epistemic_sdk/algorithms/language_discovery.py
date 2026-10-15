"""Language construction + program discovery from examples (the generalized loop).

Given training examples and a base language (the primitive operators), enumerate
the programs consistent with them, validate on an independent case, and — if the
corroborated program is not already a primitive — lift it into a new operator
(defining the language). This is the reusable form of the boolean/fuzzy
experiments: it works for any function over a finite domain, not a hardcoded
target.
"""
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from epistemic_sdk import LanguageM2
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

from .operator_invention import OperatorInvention
from .semantic_equivalence import SemanticEquivalence
from .synthesis import enumerate_terms


@dataclass(frozen=True)
class DiscoveryResult:
    program: Term | None
    language: LanguageM2
    corroborated: tuple[Term, ...]
    refuted: tuple[Term, ...]


class LanguageDiscovery:
    def __init__(
        self,
        base_language: LanguageM2,
        variables: tuple[str, ...],
        evaluate: Callable[[Term, Mapping[str, Any]], Any],
        domain: Sequence[Any],
        *,
        max_nodes: int = 9,
    ) -> None:
        self._base_language = base_language
        self._variables = variables
        self._evaluate = evaluate
        self._domain = tuple(domain)
        self._max_nodes = max_nodes

    def discover(
        self,
        training: Sequence[tuple[Mapping[str, Any], Any]],
        test_inputs: Mapping[str, Any],
        test_output: Any,
    ) -> DiscoveryResult:
        functions = self._consistent_functions(training)
        corroborated = tuple(
            term
            for term in functions
            if self._evaluate(term, test_inputs) == test_output
        )
        refuted = tuple(
            term
            for term in functions
            if self._evaluate(term, test_inputs) != test_output
        )
        program = corroborated[0] if corroborated else None

        language = self._base_language
        if program is not None and not self._is_primitive(program):
            language = OperatorInvention().lift(
                program, language, f"op_{len(language.operators)}"
            )
        return DiscoveryResult(program, language, corroborated, refuted)

    def _consistent_functions(
        self, training: Sequence[tuple[Mapping[str, Any], Any]]
    ) -> list[Term]:
        equivalence = SemanticEquivalence(self._evaluate, self._domain)
        grammar = {op.name: len(op.arguments) for op in self._base_language.operators}
        representatives: list[Term] = []
        for term in enumerate_terms(grammar, self._variables, self._max_nodes):
            if not all(
                self._evaluate(term, inputs) == output for inputs, output in training
            ):
                continue
            if not any(equivalence.equivalent(rep, term) for rep in representatives):
                representatives.append(term)
        return representatives

    def _is_primitive(self, term: Term) -> bool:
        if isinstance(term, Application):
            names = [
                argument.name for argument in term.arguments if isinstance(argument, Variable)
            ]
            return len(names) == len(term.arguments) and len(set(names)) == len(names)
        return True
