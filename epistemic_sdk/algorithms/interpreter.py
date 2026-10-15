"""Finite-domain interpreter: evaluate an M1 program's entrypoint term.

The M2 language declares operator *signatures* only (name, arity, sort) and
carries no semantics. This module injects the finite semantics of each operator
at construction time and evaluates a declarative program's entrypoint term
bottom-up. It is an interpreter, not a rewriter: rewriting is a distinct,
upstream step applied before execution.
"""

from collections.abc import Callable, Mapping
from typing import Any

from epistemic_sdk.execution.execution_context import ExecutionContext
from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


class FiniteInterpreter:
    """Evaluate an M1 entrypoint term under injected operator semantics.

    ``semantics`` maps an operator name to a total, pure Python callable that
    gives its finite-domain meaning, e.g.
    ``{"zero": lambda: 0, "succ": lambda n: n + 1, "add": lambda a, b: a + b}``.

    Semantics are untyped by design: the injected callable is declared
    ``Callable[..., Any]`` and its result is treated opaquely by the
    interpreter. Consequently the return of the injected callable is already
    ``Any`` and no ``as Any`` cast (nor ``# type: ignore``) is used.

    Limitations: operations are assumed total, pure and compositional over a
    finite domain. Sorts and arity are NOT validated against a ``LanguageM2``,
    and no rewriting is performed here.
    """

    def __init__(self, semantics: Mapping[str, Callable[..., Any]]) -> None:
        self.semantics: dict[str, Callable[..., Any]] = dict(semantics)

    def execute(self, program: ProgramM1, context: ExecutionContext) -> Any:
        """Evaluate ``program.entrypoint`` bottom-up and return its value."""
        return self._evaluate(program.entrypoint, context)

    def _evaluate(self, term: Term, context: ExecutionContext) -> Any:
        if isinstance(term, Variable):
            try:
                return context.inputs[term.name]
            except KeyError as exc:
                raise KeyError(
                    f"variable '{term.name}' is unbound in the execution context"
                ) from exc

        if isinstance(term, Constant):
            return term.value

        if isinstance(term, Application):
            arguments = tuple(
                self._evaluate(argument, context) for argument in term.arguments
            )
            try:
                operation = self.semantics[term.operator]
            except KeyError as exc:
                raise KeyError(
                    f"operator '{term.operator}' has no injected semantics"
                ) from exc
            return operation(*arguments)

        raise TypeError(f"unrecognized term node: {type(term).__name__}")
