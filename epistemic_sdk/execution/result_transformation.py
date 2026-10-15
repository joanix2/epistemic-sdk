from typing import Protocol, TypeVar

R = TypeVar("R")

class ResultTransformation(Protocol[R]):
    """Post-processing R -> R; does not modify the hypothetical program."""
    @property
    def name(self) -> str:
        ...

    def transform(self, result: R) -> R:
        ...
