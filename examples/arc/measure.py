"""ARC measurement harness: sweep training tasks and report resolution rates.

Runs the grid-transformation discovery loop (``examples.arc.discovery``) over a
set of ARC training tasks and aggregates how many are solved, broken down by the
primary transformation family of the discovered program and by every family
participating in a solved program.

This module is a *measurement* tool: it never hardcodes a task id or an expected
result, and it does not participate in discovery itself.
"""
import argparse
import json
import os
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from examples.arc.discovery import discover_task
from examples.arc.loader import Task, load_training_tasks

DEFAULT_DATA_DIR = "/home/joan/Documents/Programation/ARC-AGI/data/training"


@dataclass(frozen=True)
class MeasurementReport:
    """Aggregated resolution statistics over a set of tasks."""

    total: int
    solved: int
    by_family: tuple[tuple[str, int], ...]
    participation: tuple[tuple[str, int], ...]


def measure(tasks: Sequence[Task], *, max_nodes: int = 3) -> MeasurementReport:
    """Run discovery on every task and aggregate resolution rates.

    ``by_family`` counts ``discovery.family`` for solved tasks (the seven
    fundamental families plus ``"composition"``/``"identity"`` when they occur),
    sorted by family name. ``participation`` counts each family appearing in a
    solved program's ``families_used``.
    """
    by_family: Counter[str] = Counter()
    participation: Counter[str] = Counter()
    solved = 0
    for task in tasks:
        discovery = discover_task(task, max_nodes=max_nodes)
        if not discovery.solved:
            continue
        solved += 1
        if discovery.family is not None:
            by_family[discovery.family] += 1
        for family in discovery.families_used:
            participation[family] += 1
    return MeasurementReport(
        total=len(tasks),
        solved=solved,
        by_family=tuple(sorted(by_family.items())),
        participation=tuple(sorted(participation.items())),
    )


def _pct(part: int, whole: int) -> float:
    return part * 100.0 / whole if whole else 0.0


def format_report(report: MeasurementReport) -> str:
    """Render a ``MeasurementReport`` as a plain-text multi-line string."""
    lines = [
        f"solved {report.solved}/{report.total} "
        f"({_pct(report.solved, report.total):.1f}%)"
    ]
    lines.append("by family:")
    for family, count in report.by_family:
        lines.append(f"  {family}: {count} ({_pct(count, report.total):.1f}%)")
    lines.append("participation:")
    for family, count in report.participation:
        lines.append(f"  {family}: {count}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="examples.arc.measure",
        description="Sweep ARC training tasks and report resolution per transformation family.",
    )
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("ARC_DATA_DIR", DEFAULT_DATA_DIR),
        help="directory of ARC training task JSON files (default: $ARC_DATA_DIR or %(default)s)",
    )
    parser.add_argument(
        "--max-nodes", type=int, default=3, help="max program size passed to discover_task"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="evaluate only the first N tasks"
    )
    parser.add_argument("--json", metavar="PATH", help="also write the report as JSON")
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"ARC data directory not found: {data_dir}", file=sys.stderr)
        return 2

    tasks = load_training_tasks(data_dir)
    if args.limit is not None:
        tasks = tasks[: args.limit]

    report = measure(tasks, max_nodes=args.max_nodes)
    print(format_report(report))

    if args.json:
        Path(args.json).write_text(json.dumps(asdict(report), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
