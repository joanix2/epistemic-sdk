from typing import Protocol, TypeVar

from .execution_context import ExecutionContext

P = TypeVar("P", contravariant=True)
R = TypeVar("R", covariant=True)

class Executor(Protocol[P, R]):
    """Evaluate a transformed declarative program against its context."""
    def execute(self, program: P, context: ExecutionContext) -> R:
        ...
