"""Audit archived ARC predictions against data, without running or tuning search."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.arc.loader import load_training_tasks  # noqa: E402
from examples.arc.transfer_measure import dataset_digest, source_digest  # noqa: E402


def audit(reports: Path, data_root: Path) -> dict[str, Any]:
    manifest = json.loads((reports / "source-audit.json").read_text())
    assert source_digest() == manifest["final_source_sha256"], "source changed since audit"
    assert manifest["executed_ast_sha256"] == manifest["final_ast_sha256"]
    memory = (reports / "memory.json").read_text().rstrip("\n")
    memory_hash = hashlib.sha256(memory.encode()).hexdigest()
    summaries: dict[str, Any] = {}
    by_name: dict[str, Any] = {}
    for split in ("training", "evaluation"):
        directory = data_root / split
        tasks = {task.id: task for task in load_training_tasks(directory)}
        digest = dataset_digest(directory)
        for path in sorted(reports.glob(f"{split}-*.json")):
            report = json.loads(path.read_text())
            rows = report["tasks"]
            assert report["source_sha256"] == manifest["executed_source_sha256"]
            assert report["dataset_sha256"] == digest, path
            assert len(rows) == len(tasks) == report["total"] == 400, path
            assert len({row["task_id"] for row in rows}) == len(rows), path
            for row in rows:
                task = tasks[row["task_id"]]
                if report["mode"] != "global":
                    predictions = row["predictions"]
                    matches = [
                        prediction == [list(line) for line in example.output.cells]
                        for prediction, example in zip(predictions, task.test, strict=False)
                    ]
                    solved = len(predictions) == len(task.test) and bool(matches) and all(matches)
                    assert solved == row["solved"], (path, task.id)
                    assert len(row["validations"]) == len(predictions)
                    for index, (match, validation) in enumerate(
                        zip(matches, row["validations"], strict=True)
                    ):
                        assert (validation["status"] == "corroborated") == match
                        key = "supporting_observation_ids" if match else "counterexample_ids"
                        assert validation[key] == [f"{task.id}:test:{index}"]
                    assert row["candidates"] <= report["max_candidates"]
            assert sum(row["solved"] for row in rows) == report["solved"], path
            if report["mode"] in ("transfer", "flat-memory"):
                assert report["memory_sha256"] == memory_hash
            summaries[path.stem] = {key: report[key] for key in (
                "solved", "total", "score_percent", "candidates", "reused_tasks",
                "reused_solved", "seconds",
            )}
            by_name[path.stem] = {row["task_id"]: row for row in rows}
    comparisons = {}
    for cold, warm in (("taxonomy", "transfer"), ("flat", "flat-memory")):
        a, b = by_name[f"evaluation-{cold}"], by_name[f"evaluation-{warm}"]
        comparisons[f"{cold}_to_{warm}"] = {
            "gained": [key for key in a if b[key]["solved"] and not a[key]["solved"]],
            "lost": [key for key in a if a[key]["solved"] and not b[key]["solved"]],
            "reused": [{"task_id": key, "solved": b[key]["solved"],
                        "cold_candidates": a[key]["candidates"],
                        "warm_candidates": b[key]["candidates"]}
                       for key in a if b[key]["reused"]],
        }
    return {"summaries": summaries, "comparisons": comparisons,
            "memory_sha256": memory_hash, "prediction_audit": "passed"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=ROOT / "docs/experiments/arc-taxonomy")
    parser.add_argument("--data-root", type=Path,
                        default=Path("/home/joan/Documents/Programation/ARC-AGI/data"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.reports, args.data_root)
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload)
    print(payload)


if __name__ == "__main__":
    main()
