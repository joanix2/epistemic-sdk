from dataclasses import dataclass


@dataclass(frozen=True)
class Sort:
    """Named type (sort) in an algebraic signature."""
    name: str
