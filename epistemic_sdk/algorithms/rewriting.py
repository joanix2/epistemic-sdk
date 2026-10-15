"""Bounded term rewriting over M3 terms.

This module provides a *bounded* first-order term-rewriting engine for M3
:data:`epistemic_sdk.m3.term.Term` structures. It is deliberately bounded and
makes no claim of termination, confluence, or normalization: a rewrite run stops
either because no candidate rule matches (a normal form was reached), or because
``limit`` rule applications have been consumed (the run was cut short before
reaching any normal form).

The engine is a rewriter, not an interpreter: it mechanically transforms a
program's entrypoint term using its candidate rewrite rules and leaves the
assignment of semantics to a separate, downstream execution step.
"""

from epistemic_sdk.execution.program_transformation import ProgramTransformation
from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.rewrite_rule import RewriteRule
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


def matches(pattern: Term, term: Term) -> dict[str, Term] | None:
    """Match ``pattern`` against ``term``, returning a binding or ``None``.

    This is single-sided, first-order matching: only ``pattern`` may contain
    variables; ``term`` is treated as ground. Rules:

    * A :class:`Variable` in ``pattern`` binds to any subterm of ``term``,
      keyed by the variable *name* (``str``), not by object identity.
    * Two different :class:`Variable` objects sharing a name must bind to equal
      subterms (occurrence check); otherwise the match fails.
    * A :class:`Constant` matches only an equal :class:`Constant` — same value
      and same sort.
    * An :class:`Application` matches an :class:`Application` with the same
      operator and an equal number of arguments, matched positionally.

    Returns the mapping from variable names to matched subterms on success, or
    ``None`` when no match exists.
    """
    binding: dict[str, Term] = {}
    if _match(pattern, term, binding):
        return binding
    return None


def _match(pattern: Term, term: Term, binding: dict[str, Term]) -> bool:
    """Recursive worker for :func:`matches`, threading ``binding`` in place."""
    if isinstance(pattern, Variable):
        if pattern.name in binding:
            return binding[pattern.name] == term
        binding[pattern.name] = term
        return True

    if isinstance(pattern, Constant):
        if not isinstance(term, Constant):
            return False
        # Type-aware equality: Python's `bool` is a subclass of `int`, so plain
        # `==` would conflate `False` with `0` and `True` with `1` (and `1` with
        # `1.0`). Two constants match only if their values share the exact type.
        return (
            type(pattern.value) is type(term.value)
            and pattern.value == term.value
            and pattern.sort == term.sort
        )

    # `pattern` is an Application at this point.
    if not isinstance(term, Application):
        return False
    if pattern.operator != term.operator:
        return False
    if len(pattern.arguments) != len(term.arguments):
        return False
    for pattern_arg, term_arg in zip(pattern.arguments, term.arguments, strict=True):
        if not _match(pattern_arg, term_arg, binding):
            return False
    return True


def substitute(term: Term, binding: dict[str, Term]) -> Term:
    """Replace every bound variable in ``term``, returning a new term.

    A :class:`Variable` whose name is present in ``binding`` is replaced by the
    bound subterm; unbound variables and :class:`Constant` values are left
    unchanged. :class:`Application` nodes are recursed into and rebuilt. The
    input ``term`` is never mutated — all :class:`Term` nodes are frozen — and a
    fresh :class:`Application` is produced whenever any argument changes.
    """
    if isinstance(term, Variable):
        return binding.get(term.name, term)

    if isinstance(term, Constant):
        return term

    # `term` is an Application at this point.
    new_arguments = tuple(substitute(arg, binding) for arg in term.arguments)
    return Application(operator=term.operator, arguments=new_arguments)


def _reduce_once(term: Term, rules: tuple[RewriteRule, ...]) -> Term | None:
    """Apply a single leftmost-innermost rewrite step, or return ``None``.

    Strategy: recurse into arguments first (innermost), scanning them left to
    right (leftmost). Only when no argument contains a redex do the rules get
    matched against the term itself. Returns the term with exactly one rule
    applied, or ``None`` if no redex was found anywhere.
    """
    if isinstance(term, Application):
        for index, argument in enumerate(term.arguments):
            reduced = _reduce_once(argument, rules)
            if reduced is not None:
                new_arguments = list(term.arguments)
                new_arguments[index] = reduced
                return Application(operator=term.operator, arguments=tuple(new_arguments))

    for rule in rules:
        binding = matches(rule.source, term)
        if binding is not None:
            return substitute(rule.target, binding)
    return None


class BoundedRewriter(ProgramTransformation[ProgramM1]):
    """Rewrite a program's entrypoint with its candidate rules, bounded by ``limit``.

    Applies :attr:`ProgramM1.candidate_rules` to :attr:`ProgramM1.entrypoint`
    one rule at a time using a leftmost-innermost strategy (see
    :func:`_reduce_once`), until no rule matches or ``limit`` steps have been
    consumed. Returns a new, frozen :class:`ProgramM1` carrying the rewritten
    entrypoint and the *same* ``language_id``, ``language_version`` and
    ``candidate_rules``.

    Bounds (not proofs): the run is cut off after ``limit`` rule applications,
    so the returned term may not be a normal form. Termination, confluence and
    normalization are neither claimed nor relied upon. ``limit`` counts rule
    applications and should be a non-negative integer; ``0`` performs no rewrite
    and returns the entrypoint unchanged.
    """

    def __init__(self, limit: int = 100) -> None:
        self._limit = limit

    @property
    def name(self) -> str:
        return "bounded_rewriter"

    def transform(self, program: ProgramM1) -> ProgramM1:
        current: Term = program.entrypoint
        steps = 0
        while steps < self._limit:
            reduced = _reduce_once(current, program.candidate_rules)
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
