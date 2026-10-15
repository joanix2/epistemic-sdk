"""Program transformation: eliminate double negation via the ``not(not(X)) = X`` axiom.

This is a real, semantics-preserving ``ProgramTransformation``. It reuses the
generic first-order matching/substitution machinery of
``epistemic_sdk.algorithms.rewriting`` instead of re-implementing an AST walk.
"""

from epistemic_sdk import ProgramM1, RewriteRule
from epistemic_sdk.algorithms.rewriting import matches, substitute
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term

from .boolean_language import X

DOUBLE_NEGATION_RULE = RewriteRule(source=Application("not", (Application("not", (X,)),)), target=X)


def _reduce_once(term: Term) -> Term | None:
    """Apply the double-negation rule once, leftmost-innermost, or return ``None``."""
    if isinstance(term, Application):
        for index, argument in enumerate(term.arguments):
            reduced = _reduce_once(argument)
            if reduced is not None:
                new_arguments = list(term.arguments)
                new_arguments[index] = reduced
                return Application(term.operator, tuple(new_arguments))
    binding = matches(DOUBLE_NEGATION_RULE.source, term)
    if binding is not None:
        return substitute(DOUBLE_NEGATION_RULE.target, binding)
    return None


class NotNotElimination:
    """Normalize ``not(not(T))`` into ``T``, preserving semantics and provenance."""

    name = "not_not_elimination"

    def __init__(self, limit: int = 100) -> None:
        self._limit = limit

    def transform(self, program: ProgramM1) -> ProgramM1:
        current: Term = program.entrypoint
        steps = 0
        while steps < self._limit:
            reduced = _reduce_once(current)
            if reduced is None:
                break
            current = reduced
            steps += 1
        return ProgramM1(
            language_id=program.language_id,
            language_version=program.language_version,
            entrypoint=current,
            candidate_rules=program.candidate_rules,
        )
