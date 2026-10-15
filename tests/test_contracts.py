"""Standard-library smoke tests; run with python -m unittest discover -s tests."""
import unittest
from datetime import datetime, timezone

from epistemic_sdk import (
    Application, BeliefGraph, ExecutionContext, Hypothesis, Observation,
    ProgramM1, ProgramRunner, ValidationReport, ValidationStatus,
)
from examples.nat_language import EXAMPLE, NAT

class EchoExecutor:
    def execute(self, program: ProgramM1, context: ExecutionContext) -> int:
        return context.inputs["x"]

class OffsetProgram:
    name = "pass_through"
    def transform(self, program: ProgramM1) -> ProgramM1:
        return program

class DoubleResult:
    name = "double"
    def transform(self, result: int) -> int:
        return 2 * result

class Tests(unittest.TestCase):
    def test_m2_and_m1_are_separate(self):
        self.assertEqual(NAT.id, EXAMPLE.program.language_id)
        self.assertEqual(len(EXAMPLE.program.candidate_rules), 1)
        self.assertEqual(len(NAT.axioms), 2)

    def test_runner_and_provenance(self):
        runner = ProgramRunner(
            executor=EchoExecutor(),
            transformations=[OffsetProgram()],
            result_transformations=[DoubleResult()],
        )
        result = runner.run(EXAMPLE, ExecutionContext({"x": 3}, ("o1",)))
        self.assertEqual(result.raw_output, 3)
        self.assertEqual(result.output, 6)
        self.assertEqual(result.program_transformations, ("pass_through",))
        self.assertEqual(result.result_transformations, ("double",))
        self.assertEqual(result.hypothesis_id, "H1")
        self.assertEqual(result.context.observation_ids, ("o1",))
        self.assertEqual(result.original_program, result.executed_program)

    def test_graph_and_validation_are_typed(self):
        o = Observation("o1", "sensor1", 42, datetime.now(timezone.utc))
        graph = BeliefGraph(observations=(o,))
        self.assertEqual(graph.observations[0].value, 42)
        report = ValidationReport(
            "v1", "H1", "e1", ValidationStatus.INCONCLUSIVE,
            (), (), "validator1", datetime.now(timezone.utc),
        )
        self.assertEqual(report.status, ValidationStatus.INCONCLUSIVE)

if __name__ == "__main__":
    unittest.main()
