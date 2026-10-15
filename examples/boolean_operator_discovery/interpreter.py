"""Boolean interpreter: the finite interpreter of Phase 1, pre-configured for booleans."""

from epistemic_sdk.algorithms.interpreter import FiniteInterpreter

from .boolean_language import SEMANTICS

BOOLEAN_INTERPRETER = FiniteInterpreter(SEMANTICS)

__all__ = ["BOOLEAN_INTERPRETER"]
