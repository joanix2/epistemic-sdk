"""Fixed boolean M2 language: Bool algebra with seven operators and truth-table axioms.

This module declares the *theory*, not a runtime: it fixes the sort ``Bool``,
the operators ``not``/``and``/``or``/``xor``/``nand``/``nor``/``xnor``, and their
admitted truth-table semantics as M2 equations, plus the double-negation law
``not(not(X)) = X``. It does NOT contain the answer to "which operator does the
black box implement?" — that is what the inference step must discover.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from epistemic_sdk import (
    Axiom,
    Constant,
    Equation,
    LanguageM2,
    Operator,
    ProgramM1,
    Sort,
    Variable,
)
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term

LANGUAGE_ID = "boolean"
LANGUAGE_VERSION = "1.0.0"
BOOL = "Bool"


@dataclass(frozen=True)
class BooleanSample:
    """One observed input/output case of the black box."""

    a: bool
    b: bool
    output: bool


A = Variable("A", BOOL)
B = Variable("B", BOOL)
X = Variable("X", BOOL)


def _c(value: bool) -> Constant:
    return Constant(value, BOOL)


def _app(operator: str, *arguments: Term) -> Application:
    return Application(operator, tuple(arguments))


def _not(term: Term) -> Application:
    return _app("not", term)


FALSE = _c(False)
TRUE = _c(True)

OPERATORS = (
    Operator("not", (BOOL,), BOOL),
    Operator("and", (BOOL, BOOL), BOOL),
    Operator("or", (BOOL, BOOL), BOOL),
    Operator("xor", (BOOL, BOOL), BOOL),
    Operator("nand", (BOOL, BOOL), BOOL),
    Operator("nor", (BOOL, BOOL), BOOL),
    Operator("xnor", (BOOL, BOOL), BOOL),
)


def _truth_table(operator: str, rows: tuple[bool, bool, bool, bool]) -> tuple[Axiom, ...]:
    """Build the four ground equations defining ``operator``'s truth table.

    ``rows`` is indexed by (a, b) in the order (F, F), (F, T), (T, F), (T, T).
    """
    cases = ((False, False), (False, True), (True, False), (True, True))
    axioms: list[Axiom] = []
    for (a, b), result in zip(cases, rows, strict=True):
        lhs = _app(operator, _c(a), _c(b))
        rhs = _c(result)
        axioms.append(Axiom(f"{operator}_{int(a)}{int(b)}", Equation(lhs, rhs), "definition"))
    return tuple(axioms)


AXIOMS = (
    Axiom("not_false", Equation(_not(FALSE), TRUE), "definition"),
    Axiom("not_true", Equation(_not(TRUE), FALSE), "definition"),
    Axiom("double_negation", Equation(_not(_not(X)), X), "definition"),
    *_truth_table("and", (False, False, False, True)),
    *_truth_table("or", (False, True, True, True)),
    *_truth_table("xor", (False, True, True, False)),
    *_truth_table("nand", (True, True, True, False)),
    *_truth_table("nor", (True, False, False, False)),
    *_truth_table("xnor", (True, False, False, True)),
)

BOOLEAN_LANGUAGE = LanguageM2(
    id=LANGUAGE_ID,
    version=LANGUAGE_VERSION,
    sorts=(Sort(BOOL),),
    operators=OPERATORS,
    axioms=AXIOMS,
)

# Executable form of the truth tables (mirrors the axioms above). This is the
# finite semantics injected into the Phase 1 ``FiniteInterpreter``.
SEMANTICS: Mapping[str, Callable[..., bool]] = {
    "not": lambda x: not x,
    "and": lambda a, b: a and b,
    "or": lambda a, b: a or b,
    "xor": lambda a, b: a != b,
    "nand": lambda a, b: not (a and b),
    "nor": lambda a, b: not (a or b),
    "xnor": lambda a, b: a == b,
}

CANDIDATE_OPERATORS = ("and", "or", "xor", "nand", "nor", "xnor")


def build_program(operator: str) -> ProgramM1:
    """Build the M1 candidate program ``not(not(operator(A, B)))``.

    The double negation is deliberate: it exercises the ``NotNotElimination``
    program transformation, which must normalize it to ``operator(A, B)``.
    """
    core = _app(operator, A, B)
    return ProgramM1(
        language_id=LANGUAGE_ID,
        language_version=LANGUAGE_VERSION,
        entrypoint=_not(_not(core)),
    )
