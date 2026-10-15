"""Operator invention: lift a sub-expression into a new operator (abstraction discovery).

This is the first concrete step of problem #4 (automatic definition of M2). When
a synthesized program is long or recurring, its entrypoint can be *lifted* into
a named operator with a defining axiom; the language version is bumped so that
dependent results are invalidated (provenance preserved). The active loop's
``abduire`` action can then re-run the search in the enlarged language instead
of merely signalling exhaustion.
"""
from epistemic_sdk import Axiom, Equation, LanguageM2, Operator
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


class OperatorInvention:
    """Lift a term into a new operator defined by an axiom."""

    def lift(
        self,
        term: Term,
        language: LanguageM2,
        operator_name: str,
    ) -> LanguageM2:
        variables = self._free_variables(term)
        if not variables:
            raise ValueError("cannot lift a ground term into an operator")

        operator = Operator(
            name=operator_name,
            arguments=tuple(variable.sort for variable in variables),
            result=self._result_sort(variables),
        )
        axiom = Axiom(
            id=f"{operator_name}_def",
            statement=Equation(
                Application(operator_name, tuple(variables)),
                term,
            ),
            origin="definition",
        )
        return LanguageM2(
            id=language.id,
            version=self._bump_version(language.version),
            sorts=language.sorts,
            operators=language.operators + (operator,),
            axioms=language.axioms + (axiom,),
            subsorts=language.subsorts,
        )

    def _free_variables(self, term: Term) -> tuple[Variable, ...]:
        seen: list[Variable] = []

        def collect(node: Term) -> None:
            if isinstance(node, Variable):
                if not any(variable.name == node.name for variable in seen):
                    seen.append(node)
            elif isinstance(node, Application):
                for argument in node.arguments:
                    collect(argument)

        collect(term)
        return tuple(seen)

    def _result_sort(self, variables: tuple[Variable, ...]) -> str:
        sorts = {variable.sort for variable in variables}
        return next(iter(sorts)) if len(sorts) == 1 else "S"

    def _bump_version(self, version: str) -> str:
        parts = version.split(".")
        if parts and parts[0].isdigit():
            parts[0] = str(int(parts[0]) + 1)
            return ".".join(parts)
        return f"{version}.1"
