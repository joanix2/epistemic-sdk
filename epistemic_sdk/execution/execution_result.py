from dataclasses import dataclass
from typing import Generic, TypeVar

from .execution_context import ExecutionContext

P = TypeVar("P")
R = TypeVar("R")

@dataclass(frozen=True)
class ExecutionResult(Generic[P, R]):
    """Immutable provenance of preprocessing, execution and postprocessing."""
    id: str
    hypothesis_id: str
    original_program: P
    executed_program: P
    raw_output: R
    output: R
    context: ExecutionContext
    program_transformations: tuple[str, ...] = ()
    result_transformations: tuple[str, ...] = ()
