"""ARC task loading and grid representation.

ARC (Abstraction and Reasoning Corpus) tasks are JSON files of ``train`` and
``test`` examples; each example pairs an input grid with an output grid. A grid
is a 2D array of colors 0-9 (0 = background/black). This module provides an
immutable, hashable ``Grid`` value type and loaders for the task files.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from epistemic_sdk.algorithms.grid_objects import Grid as Grid


@dataclass(frozen=True)
class Example:
    input: Grid
    output: Grid


@dataclass(frozen=True)
class Task:
    id: str
    train: tuple[Example, ...]
    test: tuple[Example, ...]


def _grid(rows: list[list[int]]) -> Grid:
    return Grid(tuple(tuple(row) for row in rows))


def load_task(path: str | Path) -> Task:
    data = json.loads(Path(path).read_text())
    return Task(
        id=Path(path).stem,
        train=tuple(
            Example(_grid(example["input"]), _grid(example["output"]))
            for example in data["train"]
        ),
        test=tuple(
            Example(_grid(example["input"]), _grid(example["output"]))
            for example in data["test"]
        ),
    )


def load_training_tasks(data_dir: str | Path) -> tuple[Task, ...]:
    paths = sorted(Path(data_dir).glob("*.json"))
    return tuple(load_task(path) for path in paths)
