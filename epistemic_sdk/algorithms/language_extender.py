"""Invent a new operator by lifting an expression into the language.

The first step of problem #4 (automatic definition of the search subspace): when
the current language cannot express the data compactly — the ``abduire`` action
of the active loop — lift a recurring sub-expression into a new operator, adding
it (with its defining axiom) to a version-bumped ``LanguageM2``. This is the
compression move of minimum-description-length language evolution: the new
operator lets a long program be rewritten as a short one.
"""
from epistemic_sdk import Axiom, Equation, LanguageM2, Operator, Variable
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term


def _bump_version(version: str) -> str:
    parts = version.split(".")
    if parts and parts[-1].isdigit():
        parts[-1] = str(int(parts[-1]) + 1)
    else:
        parts.append("1")
    return ".".join(parts)


class LanguageExtender:
    """Extend a language with a new operator defined by a lifted expression."""

    def extend(
        self,
        language: LanguageM2,
        name: str,
        expression: Term,
        variables: tuple[str, ...],
        sort: str,
    ) -> LanguageM2:
        if any(operator.name == name for operator in language.operators):
            raise ValueError(f"operator '{name}' already exists in the language")
        variable_terms = tuple(Variable(v, sort) for v in variables)
        definition = Equation(
            left=Application(name, variable_terms),
            right=expression,
        )
        operator = Operator(name, tuple(sort for _ in variables), sort)
        axiom = Axiom(f"{name}_def", definition, "definition")
        return LanguageM2(
            id=language.id,
            version=_bump_version(language.version),
            sorts=language.sorts,
            operators=(*language.operators, operator),
            axioms=(*language.axioms, axiom),
            subsorts=language.subsorts,
        )
