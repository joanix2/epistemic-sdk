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
from .typed_search import EnumerationBudget, EnumerationLimit, enumerate_typed_terms


@dataclass(frozen=True)
class FitResult:
    """Training-only selection; consistency does not imply corroboration.

    ``exhausted`` is true only if the entire bounded search was visited.
    Candidate count measures tested result terms, not interpreter calls.
    """

    program: Term | None
    candidates: tuple[Term, ...]
    evaluated: int
    exhausted: bool
    generated: int = 0


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
        variable_sorts: Mapping[str, str] | None = None,
        result_sort: str | None = None,
    ) -> None:
        self._base_language = base_language
        self._variables = variables
        self._evaluate = evaluate
        self._domain = tuple(domain)
        self._max_nodes = max_nodes
        self._variable_sorts = variable_sorts
        self._result_sort = result_sort

    def fit(
        self,
        training: Sequence[tuple[Mapping[str, Any], Any]],
        *,
        max_candidates: int = 100_000,
        max_results: int = 1,
        max_generated: int = 50_000,
    ) -> FitResult:
        """Select programs without receiving any validation outputs.

        Retain distinct training-consistent programs when ``max_results > 1``.
        Domain probes are not needed here: no observational quotient is used.
        Evaluators must represent inapplicable programs by a non-output value;
        unexpected exceptions are intentionally not swallowed.
        """
        if max_candidates < 1 or max_results < 1 or max_generated < 1:
            raise ValueError("search budgets must be positive")
        if not training:
            return FitResult(None, (), 0, True)
        sorts = tuple(sort.name for sort in self._base_language.sorts)
        if self._variable_sorts is None:
            if len(sorts) != 1:
                raise ValueError("multi-sort search requires variable_sorts")
            variable_sorts: Mapping[str, str] = dict.fromkeys(self._variables, sorts[0])
        else:
            variable_sorts = self._variable_sorts
        result_sort = self._result_sort or (sorts[0] if len(sorts) == 1 else None)
        if result_sort is None:
            raise ValueError("multi-sort search requires result_sort")
        variables = tuple(Variable(name, variable_sorts[name]) for name in self._variables)
        candidates: list[Term] = []
        evaluated = 0
        budget = EnumerationBudget(max_generated)
        try:
            for term in enumerate_typed_terms(
                self._base_language, variables, result_sort, self._max_nodes, budget
            ):
                evaluated += 1
                if all(self._evaluate(term, inputs) == output for inputs, output in training):
                    candidates.append(term)
                    if len(candidates) == max_results:
                        return FitResult(candidates[0], tuple(candidates), evaluated, False,
                                         budget.generated)
                if evaluated == max_candidates:
                    return FitResult(candidates[0] if candidates else None,
                                     tuple(candidates), evaluated, False, budget.generated)
        except EnumerationLimit:
            return FitResult(candidates[0] if candidates else None, tuple(candidates),
                             evaluated, False, budget.generated)
        return FitResult(candidates[0] if candidates else None,
                         tuple(candidates), evaluated, True, budget.generated)

    def discover(
        self,
        training: Sequence[tuple[Mapping[str, Any], Any]],
        test_inputs: Mapping[str, Any],
        test_output: Any,
    ) -> DiscoveryResult:
        """Explore hypotheses using a labelled validation observation.

        This historical API selects among corroborated candidates and therefore
        uses the supplied label for model selection. For an unbiased prediction
        score use ``fit`` followed by evaluation on untouched observations.
        """
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
