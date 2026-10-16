"""Render solved (or failed) ARC tasks from a measure report as a standalone HTML page.

Read-only view: it reuses the stored predictions and never re-runs the solver.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from .loader import Task, load_task

DEFAULT_ROOT = Path("/home/joan/Documents/Programation/ARC-AGI/data")
PALETTE = ("#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00",
           "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25")
CELL = 14

STYLE = """
body{font-family:sans-serif;background:#222;color:#eee;margin:1rem}
section{border:1px solid #555;border-radius:6px;padding:.6rem;margin:1rem 0}
h2{margin:.1rem 0}.meta{color:#aaa;font-size:.85rem;margin-bottom:.5rem}
.row{display:flex;gap:.8rem;align-items:center;flex-wrap:wrap;margin:.3rem 0}
figure{margin:0;text-align:center;font-size:.75rem;color:#aaa}
svg{border:1px solid #666}.ok{color:#2ECC40}.ko{color:#FF4136}
"""


def _svg(cells: Any) -> str:
    rows = [list(row) for row in cells]
    height, width = len(rows), len(rows[0]) if rows else 0
    rects = "".join(
        f'<rect x="{x * CELL}" y="{y * CELL}" width="{CELL}" height="{CELL}" '
        f'fill="{PALETTE[value]}" stroke="#333" stroke-width=".5"/>'
        for y, row in enumerate(rows) for x, value in enumerate(row)
    )
    return f'<svg width="{width * CELL}" height="{height * CELL}">{rects}</svg>'


def _figure(label: str, cells: Any) -> str:
    body = _svg(cells) if cells is not None else "<em>no prediction</em>"
    return f"<figure>{body}<figcaption>{label}</figcaption></figure>"


def render_task(task: Task, row: dict[str, Any]) -> str:
    status = '<span class="ok">solved</span>' if row["solved"] else '<span class="ko">failed</span>'
    parts = [f"<section><h2>{html.escape(task.id)} {status}</h2>",
             f'<div class="meta">scope: {html.escape(str(row.get("scope")))} | '
             f'program: <code>{html.escape(str(row.get("program")))}</code></div>']
    for index, case in enumerate(task.train):
        parts.append('<div class="row">' + _figure(f"train {index} input", case.input.cells)
                     + "&rarr;" + _figure("output", case.output.cells) + "</div>")
    predictions = row.get("predictions") or [None] * len(task.test)
    for index, case in enumerate(task.test):
        prediction = predictions[index] if index < len(predictions) else None
        parts.append('<div class="row">' + _figure(f"test {index} input", case.input.cells)
                     + "&rarr;" + _figure("expected", case.output.cells)
                     + _figure("predicted", prediction) + "</div>")
    parts.append("</section>")
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_ROOT / "training")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scope", help="keep only tasks solved in this scope family")
    parser.add_argument("--failed", action="store_true", help="show failed tasks instead")
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    rows = [row for row in report["tasks"]
            if row["solved"] != args.failed and (not args.scope or row["scope"] == args.scope)]
    sections = [render_task(load_task(args.data_dir / f"{row['task_id']}.json"), row)
                for row in rows[:args.limit]]
    title = f"{report['mode']}: {report['solved']}/{report['total']} ({len(rows)} matching)"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(f"<!doctype html><meta charset=utf-8><title>ARC</title>"
                           f"<style>{STYLE}</style><h1>{html.escape(title)}</h1>"
                           + "".join(sections))
    print(f"{len(sections)} tasks written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
