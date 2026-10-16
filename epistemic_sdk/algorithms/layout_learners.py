"""Learners for outputs whose layout is derived from the input's layout.

Tiled arrangements of the input, per-color block expansion, combinations of equal
input parts, and reduction of blocks or separator-delimited cells to one color.
"""
from collections import Counter
from collections.abc import Callable
from functools import partial
from itertools import product

from . import grid_transforms as transforms
from .fitting import GridFunction, Training
from .grid_objects import Grid, dominant_color, object_crop, separator_cells

_DIHEDRAL: dict[str, GridFunction] = {
    "identity": lambda grid: grid,
    "flip_horizontal": transforms.flip_horizontal,
    "flip_vertical": transforms.flip_vertical,
    "rotate_180": transforms.rotate_180,
    "rotate_90": transforms.rotate_90,
    "rotate_270": transforms.rotate_270,
    "transpose": transforms.transpose,
    "anti_transpose": transforms.anti_transpose,
}
_BLANK = "blank"


def _block_ratio(training: Training) -> tuple[int, int] | None:
    """Constant integer (rows, columns) enlargement of every output over its input."""
    ratios = set()
    for source, target in training:
        if target.height % source.height or target.width % source.width:
            return None
        ratios.add((target.height // source.height, target.width // source.width))
    if len(ratios) != 1 or ratios == {(1, 1)}:
        return None
    return ratios.pop()


def _tile(grid: Grid, name: str) -> Grid:
    if name == _BLANK:
        return transforms.blank(grid.height, grid.width)
    tile = _DIHEDRAL[name](grid)
    if (tile.height, tile.width) != (grid.height, grid.width):
        raise ValueError("tile transform changes the block shape")
    return tile


def _apply_assembly(grid: Grid, plan: dict[tuple[int, int], str], rows: int, columns: int) -> Grid:
    return transforms.assemble([
        [_tile(grid, plan[row, column]) for column in range(columns)] for row in range(rows)
    ])


def fit_block_assembly(training: Training) -> GridFunction | None:
    """Output is a fixed array of blocks, each a dihedral image of the input or blank."""
    ratio = _block_ratio(training)
    if ratio is None:
        return None
    rows, columns = ratio
    plan: dict[tuple[int, int], str] = {}
    for row, column in product(range(rows), range(columns)):
        for name in (*_DIHEDRAL, _BLANK):
            try:
                if all(
                    transforms.block(target, row, column, source.height, source.width)
                    == _tile(source, name) for source, target in training
                ):
                    plan[row, column] = name
                    break
            except ValueError:
                continue
        else:
            return None
    return partial(_apply_assembly, plan=plan, rows=rows, columns=columns)


def _fractal(grid: Grid, inverse: bool) -> Grid:
    blank = transforms.blank(grid.height, grid.width)
    return transforms.assemble([
        [grid if (value == 0) == inverse else blank for value in row] for row in grid.cells
    ])


def fit_fractal(training: Training) -> GridFunction | None:
    """Output places a copy of the input where an input cell is (non)background."""
    for inverse in (False, True):
        if all(_fractal(source, inverse) == target for source, target in training):
            return partial(_fractal, inverse=inverse)
    return None


def _expand(grid: Grid, table: dict[int, Grid]) -> Grid:
    if any(value not in table for row in grid.cells for value in row):
        raise ValueError("unseen color")
    return transforms.assemble([[table[value] for value in row] for row in grid.cells])


def fit_cell_expansion(training: Training) -> GridFunction | None:
    """Each input color expands to a fixed block; generalizes integer upscaling."""
    ratio = _block_ratio(training)
    if ratio is None:
        return None
    table: dict[int, Grid] = {}
    for source, target in training:
        for r, c in product(range(source.height), range(source.width)):
            block = transforms.block(target, r, c, *ratio)
            if table.setdefault(source[r, c], block) != block:
                return None
    if len(set(table.values())) < 2:
        return None
    return partial(_expand, table=table)


def _equal_parts(grid: Grid, axis: str, parts: int, separator: int) -> list[Grid]:
    length = grid.width if axis == "columns" else grid.height
    size, remainder = divmod(length - separator * (parts - 1), parts)
    if remainder or size < 1:
        raise ValueError("grid does not split evenly")
    starts = [index * (size + separator) for index in range(parts)]
    if axis == "columns":
        return [Grid(tuple(row[s:s + size] for row in grid.cells)) for s in starts]
    return [Grid(grid.cells[s:s + size]) for s in starts]


def _occupancy(pieces: list[Grid], r: int, c: int) -> tuple[bool, ...]:
    return tuple(piece[r, c] != 0 for piece in pieces)


def _combine(grid: Grid, axis: str, parts: int, separator: int,
             table: dict[tuple[bool, ...], int]) -> Grid:
    pieces = _equal_parts(grid, axis, parts, separator)
    try:
        return Grid(tuple(
            tuple(table[_occupancy(pieces, r, c)] for c in range(pieces[0].width))
            for r in range(pieces[0].height)
        ))
    except KeyError as error:
        raise ValueError("unseen occupancy pattern") from error


def _occupancy_table(training: Training, axis: str, parts: int, separator: int,
                     ) -> dict[tuple[bool, ...], int] | None:
    table: dict[tuple[bool, ...], int] = {}
    support: Counter[tuple[bool, ...]] = Counter()
    for source, target in training:
        try:
            pieces = _equal_parts(source, axis, parts, separator)
        except ValueError:
            return None
        if (pieces[0].height, pieces[0].width) != (target.height, target.width):
            return None
        for r, c in product(range(target.height), range(target.width)):
            key = _occupancy(pieces, r, c)
            if table.setdefault(key, target[r, c]) != target[r, c]:
                return None
            support[key] += 1
    if len(set(table.values())) < 2 or min(support.values()) < 2:
        return None
    return table


def fit_partition_combination(training: Training) -> GridFunction | None:
    """Output cell is a lookup on which equal parts of the input are occupied."""
    for axis, parts, separator in product(("columns", "rows"), (2, 3, 4), (0, 1)):
        table = _occupancy_table(training, axis, parts, separator)
        if table is not None:
            return partial(_combine, axis=axis, parts=parts, separator=separator, table=table)
    return None


Segmentation = Callable[[Grid], list[list[Grid]]]


def _line_cells(grid: Grid) -> list[list[Grid]]:
    return [[object_crop(region) for region in row] for row in separator_cells(grid)]


def _block_cells(grid: Grid, rows: int, columns: int) -> list[list[Grid]]:
    if grid.height % rows or grid.width % columns:
        raise ValueError("grid does not divide into blocks")
    return [[transforms.block(grid, r, c, rows, columns) for c in range(grid.width // columns)]
            for r in range(grid.height // rows)]


_REDUCERS: dict[str, Callable[[Grid], int]] = {
    "majority_nonzero": dominant_color,
    "least_common_nonzero": partial(dominant_color, least=True),
    "majority": partial(dominant_color, ignore_background=False),
    "maximum": lambda cell: max(v for row in cell.cells for v in row),
    "minimum": lambda cell: min(v for row in cell.cells for v in row),
}


def _reduce(grid: Grid, segment: Segmentation, reducer: Callable[[Grid], int]) -> Grid:
    return Grid(tuple(tuple(reducer(cell) for cell in row) for row in segment(grid)))


def _segmentations(training: Training) -> list[Segmentation]:
    """Separator lines, and equal blocks when every input is a constant multiple of its output."""
    found: list[Segmentation] = [_line_cells]
    if all(s.height % t.height == 0 and s.width % t.width == 0 for s, t in training):
        ratios = {(s.height // t.height, s.width // t.width) for s, t in training}
        if len(ratios) == 1 and ratios != {(1, 1)}:
            rows, columns = ratios.pop()
            found.append(partial(_block_cells, rows=rows, columns=columns))
    return found


def fit_block_reduction(training: Training) -> GridFunction | None:
    """One output cell per equal block or per separator-delimited cell."""
    for segment in _segmentations(training):
        for reducer in _REDUCERS.values():
            try:
                if all(_reduce(source, segment, reducer) == target for source, target in training):
                    return partial(_reduce, segment=segment, reducer=reducer)
            except ValueError:
                continue
    return None
