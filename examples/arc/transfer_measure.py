"""Reproducible ARC ablation with training-only selection and frozen source memory.

These are public ARC-AGI-1 datasets, not an official private ARC Prize score.
Source tasks contribute only their training pairs. Target answers are passed
only to the independent execution validator, after the program has been fixed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from epistemic_sdk import ExecutionContext, Hypothesis, Observation, ProgramM1, ProgramRunner
from epistemic_sdk.algorithms.enumeration_validator import ObservationValidator
from epistemic_sdk.algorithms.grid_objects import Grid
from epistemic_sdk.algorithms.taxonomic_solver import GridEvaluator, TaxonomicSolver

from .discovery import discover_task
from .loader import Task, load_training_tasks

DEFAULT_ROOT = Path("/home/joan/Documents/Programation/ARC-AGI/data")


class _Executor:
    def __init__(self, evaluate: GridEvaluator) -> None:
        self.evaluate = evaluate

    def execute(self, program: ProgramM1, context: ExecutionContext) -> Any:
        return self.evaluate(program.entrypoint, context.inputs)


def evaluate_task(solver: TaxonomicSolver, task: Task) -> dict[str, Any]:
    """Fit first, then execute and record independent validation evidence."""
    selected = solver.solve(task.id, [(case.input, case.output) for case in task.train])
    row: dict[str, Any] = {
        "task_id": task.id, "solved": False, "program": repr(selected.program),
        "scope": selected.scope.node_id if selected.scope else None,
        "language": None, "candidates": selected.evaluated,
        "attempted_scopes": list(selected.attempted_scopes),
        "reused": list(selected.reused), "predictions": [], "validations": [],
    }
    if selected.program is None or selected.snapshot is None:
        return row
    language = selected.snapshot.language
    row["language"] = {"id": language.id, "version": language.version,
                       "lineage": [[ref.node_id, ref.version]
                                   for ref in selected.snapshot.lineage]}
    hypothesis = Hypothesis(
        id=f"{task.id}:{hashlib.sha256(repr(selected.program).encode()).hexdigest()[:12]}",
        program=ProgramM1(language.id, language.version, selected.program),
        supporting_belief_ids=tuple(f"{task.id}:belief:{i}" for i in range(len(task.train))),
    )
    # Evidence behind the training beliefs can be reconstructed from this record
    # and the dataset digest. Validation observation IDs are disjoint by construction.
    row["training_evidence"] = [
        {"belief_id": f"{task.id}:belief:{i}", "observation_id": f"{task.id}:train:{i}"}
        for i in range(len(task.train))
    ]
    runner: ProgramRunner[Any] = ProgramRunner(_Executor(GridEvaluator(selected.snapshot)))
    validator: ObservationValidator[ProgramM1, Any] = ObservationValidator("arc_exact_grid")
    for index, example in enumerate(task.test):
        observation = Observation(f"{task.id}:test:{index}", "arc_target", example.output,
                                  datetime.now(timezone.utc))
        execution = runner.run(hypothesis, ExecutionContext(
            {"g": example.input}, observation_ids=(observation.id,),
        ))
        report = validator.validate(execution, (observation,))
        row["predictions"].append(execution.output.cells
                                  if isinstance(execution.output, Grid) else None)
        row["validations"].append({
            "id": report.id, "hypothesis_id": report.hypothesis_id,
            "execution_id": report.execution_id, "status": report.status.value,
            "supporting_observation_ids": list(report.supporting_observation_ids),
            "counterexample_ids": list(report.counterexample_ids),
        })
    row["solved"] = bool(task.test) and all(
        report["status"] == "corroborated" for report in row["validations"]
    )
    return row


def dataset_digest(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(directory.glob("*.json")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def source_digest() -> str:
    root = Path(__file__).resolve().parents[2]
    digest = hashlib.sha256()
    for base in (root / "epistemic_sdk", root / "examples" / "arc"):
        for path in sorted(base.rglob("*.py")):
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_ROOT / "evaluation")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_ROOT / "training")
    parser.add_argument("--mode", choices=("global", "flat", "taxonomy", "transfer",
                                           "flat-memory"), default="taxonomy")
    parser.add_argument("--max-candidates", type=int, default=5000)
    parser.add_argument("--max-nodes", type=int, default=5)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--memory-in", type=Path)
    parser.add_argument("--memory-out", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.data_dir.is_dir():
        parser.error("target dataset directory does not exist")
    tasks = load_training_tasks(args.data_dir)
    if args.limit is not None:
        tasks = tasks[:args.limit]
    if not tasks:
        parser.error("target dataset is empty")
    solver = TaxonomicSolver(max_candidates=args.max_candidates, max_nodes=args.max_nodes,
                             flat=args.mode in ("flat", "flat-memory"))
    memory_mode = args.mode in ("transfer", "flat-memory")
    if args.memory_in and not memory_mode:
        parser.error("memory-in requires transfer or flat-memory mode")
    source_tasks: tuple[Task, ...] = ()
    if memory_mode:
        if args.memory_in:
            solver.import_memory(args.memory_in.read_text())
        else:
            if not args.source_dir.is_dir():
                parser.error("source dataset directory does not exist")
            source_tasks = load_training_tasks(args.source_dir)
            if not source_tasks:
                parser.error("source dataset is empty")
            if {task.id for task in tasks} & {task.id for task in source_tasks}:
                parser.error("source and target task IDs must be disjoint")
            source = TaxonomicSolver(max_candidates=args.max_candidates, max_nodes=args.max_nodes)
            for index, task in enumerate(source_tasks):
                source.learn(task.id, [(case.input, case.output) for case in task.train])
                if (index + 1) % 50 == 0:
                    print(f"source {index + 1}/{len(source_tasks)}; "
                          f"definitions={len(source.promotions)}", flush=True)
            solver.import_memory(source.export_memory())
        origins = {origin for node in solver.taxonomy.nodes.values()
                   for learned in node.learned for origin in learned.origin_task_ids}
        if origins & {task.id for task in tasks}:
            parser.error("memory contains target task provenance")
    frozen_memory = solver.export_memory()
    if args.memory_out:
        args.memory_out.parent.mkdir(parents=True, exist_ok=True)
        args.memory_out.write_text(frozen_memory + "\n")
    rows: list[dict[str, Any]] = []
    started = time.monotonic()
    for index, task in enumerate(tasks):
        row: dict[str, Any]
        if args.mode == "global":
            result = discover_task(task, max_nodes=3)
            row = {"task_id": task.id, "solved": result.solved,
                   "scope": result.family, "program": repr(result.program), "reused": []}
        else:
            row = evaluate_task(solver, task)
        rows.append(row)
        if (index + 1) % 50 == 0:
            print(f"target {index + 1}/{len(tasks)}; solved="
                  f"{sum(row['solved'] for row in rows)}", flush=True)
    if solver.export_memory() != frozen_memory:
        raise RuntimeError("reusable memory changed during target evaluation")
    solved = sum(row["solved"] for row in rows)
    report = {
        "benchmark": "public ARC-AGI-1; one selected prediction; all test pairs must match",
        "mode": args.mode, "total": len(tasks), "solved": solved,
        "score_percent": 100 * solved / len(tasks),
        "max_candidates": args.max_candidates, "max_nodes": args.max_nodes,
        "global_max_nodes": 3, "seconds": time.monotonic() - started,
        "dataset_sha256": dataset_digest(args.data_dir), "source_sha256": source_digest(),
        "memory_sha256": hashlib.sha256(frozen_memory.encode()).hexdigest(),
        "source_dataset_sha256": dataset_digest(args.source_dir) if source_tasks else None,
        "definitions": len(solver.promotions),
        "reused_tasks": sum(bool(row["reused"]) for row in rows),
        "reused_solved": sum(bool(row["reused"]) and row["solved"] for row in rows),
        "candidates": sum(row.get("candidates", 0) for row in rows),
        "by_scope": dict(Counter(row["scope"] for row in rows if row["solved"])),
        "tasks": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{args.mode}: {solved}/{len(tasks)} ({report['score_percent']:.2f}%), "
          f"reuse={report['reused_tasks']}, candidates={report['candidates']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
