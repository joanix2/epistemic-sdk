"""Elementary ARC grid transformations.

ARC tasks are input-grid -> output-grid transformations. This module provides
the elementary transformations used as the primitive operators of the grid
language: recoloring, reflections and rotations, diagonal symmetries, cropping,
integer upscaling, padding, halves, gravity and shifts, concatenation, boolean
logic on masks and dilation/erosion. Each function is pure and returns
a new ``Grid``; partial ones document ``ValueError`` for inapplicable inputs.
"""
from collections.abc import Callable, Mapping

from .grid_objects import Grid


def recolor(grid: Grid, mapping: Mapping[int, int]) -> Grid:
    return Grid(
        tuple(tuple(mapping.get(cell, cell) for cell in row) for row in grid.cells)
    )


def flip_horizontal(grid: Grid) -> Grid:
    return Grid(tuple(tuple(reversed(row)) for row in grid.cells))


def flip_vertical(grid: Grid) -> Grid:
    return Grid(tuple(reversed(grid.cells)))



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


def half(grid: Grid, part: str) -> Grid:
    """Keep a half or quadrant; a middle row/column of odd sizes is dropped."""
    vertical, _, horizontal = part.partition("_")
    if part in ("left", "right"):
        vertical, horizontal = "", part
    rows = {"top": slice(0, grid.height // 2), "bottom": slice((grid.height + 1) // 2, None),
            "": slice(None)}[vertical]
    columns = {"left": slice(0, grid.width // 2), "right": slice((grid.width + 1) // 2, None),
               "": slice(None)}[horizontal]
    return Grid(tuple(row[columns] for row in grid.cells[rows]))


def gravity(grid: Grid, direction: str) -> Grid:
    """Slide non-zero cells toward a side line by line, keeping their order."""
    if direction in ("up", "down"):
        return transpose(gravity(transpose(grid), "left" if direction == "up" else "right"))
    rows = []
    for row in grid.cells:
        packed = tuple(value for value in row if value)
        padding = (0,) * (len(row) - len(packed))
        rows.append(packed + padding if direction == "left" else padding + packed)
    return Grid(tuple(rows))


def shift(grid: Grid, direction: str) -> Grid:
    """Translate by one cell, dropping overflow and filling with 0."""
    if direction in ("up", "down"):
        return transpose(shift(transpose(grid), "left" if direction == "up" else "right"))
    zero = (0,)
    return Grid(tuple(
        row[1:] + zero if direction == "left" else zero + row[:-1] for row in grid.cells
    ))


def dedupe(grid: Grid, axis: str) -> Grid:
    """Collapse runs of identical consecutive rows, columns, or both."""
    if axis == "both":
        return dedupe(dedupe(grid, "rows"), "columns")
    if axis == "columns":
        return transpose(dedupe(transpose(grid), "rows"))
    rows = [row for index, row in enumerate(grid.cells)
            if index == 0 or row != grid.cells[index - 1]]
    return Grid(tuple(rows))


def hconcat(left: Grid, right: Grid) -> Grid:
    """Place ``right`` next to ``left``; heights must match."""
    if left.height != right.height:
        raise ValueError("heights differ")
    return Grid(tuple(a + b for a, b in zip(left.cells, right.cells, strict=True)))


def vconcat(top: Grid, bottom: Grid) -> Grid:
    """Stack ``bottom`` under ``top``; widths must match."""
    if top.width != bottom.width:
        raise ValueError("widths differ")
    return Grid(top.cells + bottom.cells)


def _combine(first: Grid, second: Grid, rule: Callable[[int, int], int]) -> Grid:
    if (first.height, first.width) != (second.height, second.width):
        raise ValueError("shapes differ")
    return Grid(tuple(
        tuple(rule(a, b) for a, b in zip(row_a, row_b, strict=True))
        for row_a, row_b in zip(first.cells, second.cells, strict=True)
    ))


def logical_and(first: Grid, second: Grid) -> Grid:
    """Keep ``first`` where both grids are non-zero."""
    return _combine(first, second, lambda a, b: a if a and b else 0)


def logical_or(first: Grid, second: Grid) -> Grid:
    """Keep ``first`` where non-zero, else ``second``."""
    return _combine(first, second, lambda a, b: a or b)


def logical_xor(first: Grid, second: Grid) -> Grid:
    """Keep the non-zero cell of whichever grid is non-zero alone."""
    return _combine(first, second, lambda a, b: a or b if not (a and b) else 0)


def logical_not(grid: Grid) -> Grid:
    """Mask inversion: background becomes 1, foreground becomes 0."""
    return Grid(tuple(tuple(0 if cell else 1 for cell in row) for row in grid.cells))


_NEIGHBORS = {4: ((-1, 0), (1, 0), (0, -1), (0, 1)),
              8: tuple((r, c) for r in (-1, 0, 1) for c in (-1, 0, 1) if (r, c) != (0, 0))}


def dilate(grid: Grid, connectivity: int) -> Grid:
    """Background cells touching foreground take its smallest neighboring color."""
    def neighbors(r: int, c: int) -> list[int]:
        return [grid.cells[r + dr][c + dc] for dr, dc in _NEIGHBORS[connectivity]
                if 0 <= r + dr < grid.height and 0 <= c + dc < grid.width
                and grid.cells[r + dr][c + dc]]
    return Grid(tuple(
        tuple(value or min(neighbors(r, c), default=0) for c, value in enumerate(row))
        for r, row in enumerate(grid.cells)
    ))


def erode(grid: Grid, connectivity: int) -> Grid:
    """Remove foreground cells touching background or the border."""
    def inside(r: int, c: int) -> bool:
        return all(0 <= r + dr < grid.height and 0 <= c + dc < grid.width
                   and grid.cells[r + dr][c + dc] for dr, dc in _NEIGHBORS[connectivity])
    return Grid(tuple(
        tuple(value if value and inside(r, c) else 0 for c, value in enumerate(row))
        for r, row in enumerate(grid.cells)
    ))
