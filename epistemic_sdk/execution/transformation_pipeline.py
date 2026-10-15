from typing import Protocol, TypeVar

P = TypeVar("P")

class TransformationPipeline(Protocol[P]):
    """Program-level transformation pipeline, independent of executor."""
    def apply(self, program: P) -> P:
        ...
