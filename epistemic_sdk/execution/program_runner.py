from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import uuid4

from epistemic_sdk.m1.hypothesis import Hypothesis
from epistemic_sdk.m1.program_m1 import ProgramM1

from .execution_context import ExecutionContext
from .execution_result import ExecutionResult
from .executor import Executor
from .program_transformation import ProgramTransformation
from .result_transformation import ResultTransformation

R = TypeVar("R")

class ProgramRunner(Generic[R]):
    """Minimal orchestration; interpreters and transformations are injected.

    The program is an M1 ProgramM1 in an M2 language. Nothing here claims
    to implement the reflective M3 runtime: supply a suitable Executor.
    """
    def __init__(
        self,
        executor: Executor[ProgramM1, R],
        transformations: Sequence[ProgramTransformation[ProgramM1]] = (),
        result_transformations: Sequence[ResultTransformation[R]] = (),
    ) -> None:
        self.executor = executor
        self.transformations = tuple(transformations)
        self.result_transformations = tuple(result_transformations)

    def run(
        self, hypothesis: Hypothesis, context: ExecutionContext
    ) -> ExecutionResult[ProgramM1, R]:
        program: ProgramM1 = hypothesis.program
        for transformation in self.transformations:
            program = transformation.transform(program)
        raw_output = self.executor.execute(program, context)
        output = raw_output
        for result_transformation in self.result_transformations:
            output = result_transformation.transform(output)
        return ExecutionResult(
            id=str(uuid4()),
            hypothesis_id=hypothesis.id,
            original_program=hypothesis.program,
            executed_program=program,
            raw_output=raw_output,
            output=output,
            context=context,
            program_transformations=tuple(t.name for t in self.transformations),
            result_transformations=tuple(t.name for t in self.result_transformations),
        )
