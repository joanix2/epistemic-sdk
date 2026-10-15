from __future__ import annotations
from typing import Protocol
from .meta_execution import MetaExecution
from .term import Term
from epistemic_sdk.m2.language_m2 import LanguageM2

class ReflectiveM3(Protocol):
    """Interface for a Maude-inspired reflective rewriting engine.

    Implementations must provide an encoding of languages and terms within
    the universal theory. Dataclasses alone do NOT implement reflection.
    """

    @property
    def universal_theory(self) -> LanguageM2:
        ...

    def check_language(self, language: LanguageM2) -> tuple[str, ...]:
        """Errors in signature, sorts, axioms; empty tuple means well-formed."""
        ...

    def quote_language(self, language: LanguageM2) -> Term:
        ...

    def quote_term(self, term: Term) -> Term:
        ...

    def unquote_term(self, encoded: Term) -> Term:
        ...

    def meta_reduce(
        self, quoted_language: Term, quoted_term: Term, *, limit: int
    ) -> MetaExecution:
        """Bounded equational reduction."""
        ...

    def meta_rewrite(
        self, quoted_language: Term, quoted_term: Term, *, limit: int
    ) -> MetaExecution:
        """Bounded rewriting modulo the chosen equational theory."""
        ...
