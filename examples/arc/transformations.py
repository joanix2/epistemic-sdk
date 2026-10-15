"""Simple grid transformations and their discovery (first ARC experiment).

ARC tasks are input-grid -> output-grid transformations. This module provides a
few elementary transformations and a discovery function for the simplest one —
recoloring — which learns the color mapping from the training examples and
applies it to unseen inputs. This is the first, deliberately minimal
demonstration of the loop on real ARC data.
"""
from collections.abc import Mapping

from .loader import Example, Grid


def recolor(grid: Grid, mapping: Mapping[int, int]) -> Grid:
    return Grid(
        tuple(tuple(mapping.get(cell, cell) for cell in row) for row in grid.cells)
    )


def flip_horizontal(grid: Grid) -> Grid:
    return Grid(tuple(tuple(reversed(row)) for row in grid.cells))


def flip_vertical(grid: Grid) -> Grid:
    return Grid(tuple(reversed(grid.cells)))


def discover_recolor(examples: tuple[Example, ...]) -> dict[int, int]:
    mapping: dict[int, int] = {}
    for example in examples:
        if (
            example.input.height != example.output.height
            or example.input.width != example.output.width
        ):
            raise ValueError("grid dimensions differ; recolor does not apply")
        for row in range(example.input.height):
            for column in range(example.input.width):
                source = example.input[row, column]
                target = example.output[row, column]
                if source == target:
                    continue
                if source in mapping and mapping[source] != target:
                    raise ValueError(f"inconsistent recolor for color {source}")
                mapping[source] = target
    return mapping
