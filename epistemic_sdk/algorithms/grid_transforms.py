"""Elementary ARC grid transformations.

ARC tasks are input-grid -> output-grid transformations. This module provides
the elementary transformations used as the primitive operators of the grid
language: recoloring, reflections and rotations, diagonal symmetries, cropping,
integer upscaling, padding, halves, gravity and shifts, plus the block helpers
used to build tiled outputs. Each function is pure and returns a new ``Grid``;
partial ones document ``ValueError`` for inapplicable inputs.
"""
from collections.abc import Collection, Mapping, Sequence

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


def blank(height: int, width: int) -> Grid:
    return Grid(tuple((0,) * width for _ in range(height)))


def block(grid: Grid, row: int, column: int, height: int, width: int) -> Grid:
    """Sub-grid at block index (row, column) for blocks of the given size."""
    return Grid(tuple(
        grid.cells[r][column * width:(column + 1) * width]
        for r in range(row * height, (row + 1) * height)
    ))


def assemble(blocks: Sequence[Sequence[Grid]]) -> Grid:
    """Concatenate a rectangular array of equally sized blocks."""
    return Grid(tuple(
        tuple(value for item in line for value in item.cells[r])
        for line in blocks for r in range(line[0].height)
    ))


def crop_to_colors(grid: Grid, colors: Collection[int], inset: int = 0) -> Grid:
    """Bounding box of the given colors, shrunk by ``inset`` cells on every side."""
    found = [(r, c) for r, row in enumerate(grid.cells) for c, value in enumerate(row)
             if value in colors]
    if not found:
        raise ValueError("no cell of the requested colors")
    top, bottom = min(r for r, _ in found) + inset, max(r for r, _ in found) + 1 - inset
    left, right = min(c for _, c in found) + inset, max(c for _, c in found) + 1 - inset
    if top >= bottom or left >= right:
        raise ValueError("inset leaves an empty grid")
    return Grid(tuple(row[left:right] for row in grid.cells[top:bottom]))
