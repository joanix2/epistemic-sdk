from dataclasses import dataclass
from epistemic_sdk.m3.axiom import Axiom
from epistemic_sdk.m3.operator import Operator
from epistemic_sdk.m3.sort import Sort

@dataclass(frozen=True)
class LanguageM2:
    """Versioned declarative language defined using M3 algebraic syntax."""
    id: str
    version: str
    sorts: tuple[Sort, ...]
    operators: tuple[Operator, ...]
    axioms: tuple[Axiom, ...] = ()
    subsorts: tuple[tuple[str, str], ...] = ()
