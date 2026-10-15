"""Elementary ARC grid transformations.

ARC tasks are input-grid -> output-grid transformations. This module provides
the elementary transformations used as the primitive operators of the grid
language: recoloring (with its mapping learned from training examples),
reflections and rotations, diagonal symmetries, cropping to the non-background
bounding box, integer upscaling and square padding. Each function is pure and
returns a new ``Grid``; the dimension-changing ones (crop, upscale, pad_square)
do not preserve size.
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


def rotate_90(grid: Grid) -> Grid:
    """Rotate 90 degrees clockwise: out[i][j] = in[h-1-j][i]."""
    height, width = grid.height, grid.width
    return Grid(
        tuple(
            tuple(grid.cells[height - 1 - column][row] for column in range(height))
            for row in range(width)
        )
    )


def rotate_180(grid: Grid) -> Grid:
    """Rotate 180 degrees: reverse the rows and reverse each row."""
    return Grid(tuple(tuple(reversed(row)) for row in reversed(grid.cells)))


def rotate_270(grid: Grid) -> Grid:
    """Rotate 270 degrees clockwise (== 90 counter-clockwise): out[i][j] = in[j][w-1-i]."""
    width = grid.width
    return Grid(
        tuple(
            tuple(grid.cells[column][width - 1 - row] for column in range(grid.height))
            for row in range(width)
        )
    )


def transpose(grid: Grid) -> Grid:
    """Reflect across the main diagonal: out[i][j] = in[j][i]."""
    return Grid(
        tuple(
            tuple(grid.cells[column][row] for column in range(grid.height))
            for row in range(grid.width)
        )
    )


def anti_transpose(grid: Grid) -> Grid:
    """Reflect across the anti-diagonal; implemented as transpose(rotate_180(grid))."""
    return transpose(rotate_180(grid))


def crop(grid: Grid) -> Grid:
    """Remove outer rows/columns that are entirely background (0).

    Returns the bounding box of all non-zero cells. If no non-zero cell exists,
    returns the original grid unchanged (no-op convention).
    """
    non_zero = [
        (row, column)
        for row, cells in enumerate(grid.cells)
        for column, value in enumerate(cells)
        if value != 0
    ]
    if not non_zero:
        return grid
    min_row = min(row for row, _ in non_zero)
    max_row = max(row for row, _ in non_zero)
    min_column = min(column for _, column in non_zero)
    max_column = max(column for _, column in non_zero)
    return Grid(
        tuple(
            tuple(grid.cells[row][column] for column in range(min_column, max_column + 1))
            for row in range(min_row, max_row + 1)
        )
    )


def upscale(grid: Grid, factor: int) -> Grid:
    """Replace each cell by a ``factor`` x ``factor`` block of that value."""
    if factor < 1:
        raise ValueError(f"factor must be >= 1, got {factor}")
    return Grid(
        tuple(
            tuple(value for value in row for _ in range(factor))
            for row in grid.cells
            for _ in range(factor)
        )
    )


def pad_square(grid: Grid) -> Grid:
    """Pad with background 0 on the right and bottom to a square of side max(h, w)."""
    side = max(grid.height, grid.width)
    padded = [row + (0,) * (side - grid.width) for row in grid.cells]
    padded.extend((0,) * side for _ in range(side - grid.height))
    return Grid(tuple(padded))
