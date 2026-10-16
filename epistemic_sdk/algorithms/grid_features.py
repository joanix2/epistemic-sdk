"""Per-cell descriptors for learning local recoloring rules.

A descriptor summarizes the neighborhood or the object context of one cell. It is
a pure function of the input grid and carries no knowledge of any task. Learners
decide which descriptor, if any, explains a set of training pairs.
"""
from collections import Counter
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from functools import cached_property

from .grid_objects import Grid, components, fill_holes

ORTHOGONAL = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIAGONAL = ((-1, -1), (-1, 1), (1, -1), (1, 1))
SQUARE = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1))
OUTSIDE = -1
_ENCLOSED = 10  # marker color absent from ARC palettes, used to flag enclosed background


@dataclass(frozen=True)
class CellView:
    """A cell's color, its descriptor value, and colors an output may copy from it."""

    color: int
    descriptor: Hashable
    candidates: tuple[int, ...] = ()

    @property
    def key(self) -> tuple[int, Hashable]:
        return self.color, self.descriptor


@dataclass(frozen=True)
class ObjectFacts:
    size: int
    is_largest: bool
    is_smallest: bool
    touches_border: bool


NO_OBJECT = ObjectFacts(0, False, False, False)


def ray(grid: Grid, row: int, column: int, delta_row: int, delta_column: int) -> int:
    """First non-zero color met when walking away from a cell; 0 if none."""
    row, column = row + delta_row, column + delta_column
    while 0 <= row < grid.height and 0 <= column < grid.width:
        if grid[row, column]:
            return grid[row, column]
        row, column = row + delta_row, column + delta_column
    return 0


def around(
    grid: Grid, row: int, column: int, offsets: tuple[tuple[int, int], ...],
) -> tuple[int, ...]:
    return tuple(
        grid[row + dr, column + dc]
        if 0 <= row + dr < grid.height and 0 <= column + dc < grid.width else OUTSIDE
        for dr, dc in offsets
    )


class _Context:
    """Lazily computed whole-grid facts shared by the descriptors of one grid."""

    def __init__(self, grid: Grid) -> None:
        self.grid = grid

    @cached_property
    def objects(self) -> dict[tuple[int, int], ObjectFacts]:
        found = components(self.grid, 0, 4, True)
        largest = max((obj.size for obj in found), default=0)
        smallest = min((obj.size for obj in found), default=0)
        facts = {}
        for obj in found:
            top, left, bottom, right = obj.bbox
            border = (top == 0 or left == 0 or bottom == self.grid.height
                      or right == self.grid.width)
            for row, column, _ in obj.cells:
                facts[row, column] = ObjectFacts(
                    obj.size, obj.size == largest, obj.size == smallest, border)
        return facts

    @cached_property
    def size_ranks(self) -> dict[int, int]:
        sizes = sorted({facts.size for facts in self.objects.values()}, reverse=True)
        return {size: index for index, size in enumerate(sizes)}

    @cached_property
    def color_ranks(self) -> dict[int, int]:
        counts = Counter(v for row in self.grid.cells for v in row if v)
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return {color: index for index, (color, _) in enumerate(ordered)}

    @cached_property
    def holes(self) -> Grid:
        return fill_holes(self.grid, _ENCLOSED)

    @cached_property
    def row_colors(self) -> list[frozenset[int]]:
        return [frozenset(v for v in row if v) for row in self.grid.cells]

    @cached_property
    def column_colors(self) -> list[frozenset[int]]:
        grid = self.grid
        return [frozenset(grid[r, c] for r in range(grid.height) if grid[r, c])
                for c in range(grid.width)]

    def facts(self, r: int, c: int) -> ObjectFacts:
        return self.objects.get((r, c), NO_OBJECT)

    def rays(self, r: int, c: int, offsets: tuple[tuple[int, int], ...] = ORTHOGONAL,
             ) -> tuple[int, ...]:
        return tuple(ray(self.grid, r, c, dr, dc) for dr, dc in offsets)

    def mirrors(self, r: int, c: int) -> tuple[int, ...]:
        grid = self.grid
        return (grid[r, grid.width - 1 - c], grid[grid.height - 1 - r, c],
                grid[grid.height - 1 - r, grid.width - 1 - c])

    def neighbors(self, r: int, c: int, offsets: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
        return around(self.grid, r, c, offsets)


Plain = Callable[[_Context, int, int], Hashable]
Relational = Callable[[_Context, int, int], tuple[Hashable, tuple[int, ...]]]


def _between(ctx: _Context, r: int, c: int) -> tuple[Hashable, tuple[int, ...]]:
    up, down, left, right = ctx.rays(r, c)
    return (left == right != 0, up == down != 0), (left, up)


def _present(values: tuple[int, ...]) -> tuple[bool, ...]:
    return tuple(value > 0 for value in values)


_PLAIN: dict[str, Plain] = {
    "color": lambda ctx, r, c: 0,
    "parity": lambda ctx, r, c: (r % 2, c % 2),
    "neighbors_4_count": lambda ctx, r, c: sum(_present(ctx.neighbors(r, c, ORTHOGONAL))),
    "neighbors_8_count": lambda ctx, r, c: sum(
        _present(ctx.neighbors(r, c, ORTHOGONAL + DIAGONAL))),
    "enclosed": lambda ctx, r, c: ctx.holes[r, c] == _ENCLOSED,
    "object_extremes": lambda ctx, r, c: (ctx.facts(r, c).is_largest, ctx.facts(r, c).is_smallest),
    "neighbor_sets": lambda ctx, r, c: (
        frozenset(ctx.neighbors(r, c, ORTHOGONAL)) - {0, OUTSIDE},
        frozenset(ctx.neighbors(r, c, DIAGONAL)) - {0, OUTSIDE}),
    "object_border": lambda ctx, r, c: ctx.facts(r, c).touches_border,
    "row_rays": lambda ctx, r, c: ctx.rays(r, c, ((0, -1), (0, 1))),
    "column_rays": lambda ctx, r, c: ctx.rays(r, c, ((-1, 0), (1, 0))),
    "uniform_lines": lambda ctx, r, c: (
        len(set(ctx.grid.cells[r])) == 1,
        len({ctx.grid[i, c] for i in range(ctx.grid.height)}) == 1),
    "object_size_rank": lambda ctx, r, c: ctx.size_ranks.get(ctx.facts(r, c).size, -1),
    "orthogonal_rays": lambda ctx, r, c: ctx.rays(r, c),
    "diagonal_rays": lambda ctx, r, c: ctx.rays(r, c, DIAGONAL),
    "row_column_colors": lambda ctx, r, c: (ctx.row_colors[r], ctx.column_colors[c]),
    "object_size": lambda ctx, r, c: ctx.facts(r, c).size,
    "neighbors_4": lambda ctx, r, c: ctx.neighbors(r, c, ORTHOGONAL),
    "neighbors_8": lambda ctx, r, c: ctx.neighbors(r, c, SQUARE),
    "color_rank": lambda ctx, r, c: ctx.color_ranks.get(ctx.grid[r, c], -1),
    "mirrors": lambda ctx, r, c: ctx.mirrors(r, c),
}

_RELATIONAL: dict[str, Relational] = {
    "between": _between,
    "ray_copy": lambda ctx, r, c: (_present(ctx.rays(r, c)), ctx.rays(r, c)),
    "neighbor_copy": lambda ctx, r, c: (
        _present(ctx.neighbors(r, c, ORTHOGONAL)), ctx.neighbors(r, c, ORTHOGONAL)),
    "mirror_copy": lambda ctx, r, c: (_present(ctx.mirrors(r, c)), ctx.mirrors(r, c)),
}

# Roughly increasing complexity; learners break ties on description length with it.
DESCRIPTOR_ORDER = (
    "color", "parity", "neighbors_4_count", "neighbors_8_count", "enclosed", "object_extremes",
    "neighbor_sets", "object_border", "row_rays", "column_rays", "uniform_lines",
    "object_size_rank", "orthogonal_rays", "diagonal_rays", "between", "ray_copy",
    "neighbor_copy", "mirror_copy", "row_column_colors", "object_size",
    "neighbors_4", "neighbors_8", "color_rank", "mirrors",
)


def describe(grid: Grid, name: str) -> list[list[CellView]]:
    """Descriptor ``name`` for every cell, in row-major order."""
    ctx = _Context(grid)
    if name in _PLAIN:
        plain = _PLAIN[name]
        return [[CellView(grid[r, c], plain(ctx, r, c)) for c in range(grid.width)]
                for r in range(grid.height)]
    relational = _RELATIONAL[name]
    table = []
    for r in range(grid.height):
        line = []
        for c in range(grid.width):
            value, candidates = relational(ctx, r, c)
            line.append(CellView(grid[r, c], value, candidates))
        table.append(line)
    return table
