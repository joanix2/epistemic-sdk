from dataclasses import dataclass

from .relation_type import RelationType


@dataclass(frozen=True)
class Relation:
    """Edge between observation/belief identifiers in a belief graph."""
    source_id: str
    target_id: str
    type: RelationType
    weight: float = 1.0
