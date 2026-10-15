"""Abduction: mine a fragment and lift it into a new operator (the "abduire" action).

When the active loop's hypotheses are exhausted, "abduire" expands the language:
mine the corpus of solved programs for the most compression-worthy fragment,
lift it into a new operator, and bump the language version. This is the
concrete wiring of problem #4 (automatic definition of M2) — no LLM.
"""
from collections.abc import Sequence

from epistemic_sdk import LanguageM2
from epistemic_sdk.m3.term import Term

from .abstraction_discovery import AbstractionDiscovery
from .operator_invention import OperatorInvention


class AbductionOperator:
    """The "abduire" action: mine, lift, version."""

    def __init__(
        self,
        discovery: AbstractionDiscovery,
        invention: OperatorInvention,
    ) -> None:
        self._discovery = discovery
        self._invention = invention

    def abduce(
        self,
        corpus: Sequence[Term],
        language: LanguageM2,
        operator_name: str | None = None,
    ) -> LanguageM2 | None:
        best = self._discovery.best(corpus)
        if best is None:
            return None
        name = operator_name or f"op_{len(language.operators)}"
        return self._invention.lift(best.pattern, language, name)
