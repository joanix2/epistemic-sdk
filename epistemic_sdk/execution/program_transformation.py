from typing import Protocol, TypeVar

P = TypeVar("P")

class ProgramTransformation(Protocol[P]):
    """Transformation P -> P, e.g. rewrite/normalize/optimize."""
    @property
    def name(self) -> str:
        ...

    def transform(self, program: P) -> P:
        ...
