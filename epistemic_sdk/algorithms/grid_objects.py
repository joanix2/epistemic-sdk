"""Reusable finite-grid objects and transformations, independent of ARC task data.

Objects are connected foreground components under an explicit background and
connectivity convention. These conventions are hypotheses to select during
search, not assertions about a grid's intended interpretation.
"""

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Grid:
    """Immutable rectangular grid; integer colors have no intrinsic semantics."""

    cells: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if any(len(row) != self.width for row in self.cells):
            raise ValueError("Grid rows must have equal widths")

    @property
    def height(self) -> int:
        return len(self.cells)

    @property
    def width(self) -> int:
        return len(self.cells[0]) if self.cells else 0

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(sorted({cell for row in self.cells for cell in row}))

    def __getitem__(self, position: tuple[int, int]) -> int:
        row, column = position
        return self.cells[row][column]


@dataclass(frozen=True)
class GridObject:
    """Nonempty object represented by sorted absolute (row, column, color) cells."""

    cells: tuple[tuple[int, int, int], ...]

    def __post_init__(self) -> None:
        if not self.cells:
            raise ValueError("An object must contain at least one cell")
        if any(row < 0 or column < 0 for row, column, _ in self.cells):
            raise ValueError("Object coordinates must be nonnegative")
        if len({(row, column) for row, column, _ in self.cells}) != len(self.cells):
            raise ValueError("An object cannot contain duplicate positions")
        object.__setattr__(self, "cells", tuple(sorted(self.cells)))

    @property
    def size(self) -> int:
        return len(self.cells)

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(sorted({color for _, _, color in self.cells}))

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        """Bounding box (top, left, bottom, right), with exclusive ends."""
        rows = [row for row, _, _ in self.cells]
        columns = [column for _, column, _ in self.cells]
        return min(rows), min(columns), max(rows) + 1, max(columns) + 1

    @property
    def height(self) -> int:
        top, _, bottom, _ = self.bbox
        return bottom - top

    @property
    def width(self) -> int:
        _, left, _, right = self.bbox
        return right - left

    @property
    def shape(self) -> tuple[tuple[int, int], ...]:
        """Translation-normalized occupied positions, ignoring color."""
        top, left, _, _ = self.bbox
        return tuple((row - top, column - left) for row, column, _ in self.cells)


def dominant_color(
    grid: Grid, ignore_background: bool = True, least: bool = False, background: int = 0,
) -> int:
    """Most (or least) frequent color; ties take the smallest color, empty gives background."""
    counts = Counter(value for row in grid.cells for value in row
                     if not (ignore_background and value == background))
    if not counts:
        return background
    sign = 1 if least else -1
    return min(counts.items(), key=lambda item: (sign * item[1], item[0]))[0]


def _offsets(connectivity: int) -> tuple[tuple[int, int], ...]:
    if connectivity not in (4, 8):
        raise ValueError("Connectivity must be 4 or 8")
    return tuple(
        (row, column)
        for row in (-1, 0, 1)
        for column in (-1, 0, 1)
        if (row or column) and (connectivity == 8 or abs(row) + abs(column) == 1)
    )


def components(
    grid: Grid, background: int = 0, connectivity: int = 4, monochrome: bool = True,
) -> tuple[GridObject, ...]:
    """Connected foreground objects in deterministic row-major discovery order."""
    offsets = _offsets(connectivity)
    seen: set[tuple[int, int]] = set()
    objects = []
    for row in range(grid.height):
        for column in range(grid.width):
            if (row, column) in seen or grid[row, column] == background:
                continue
            color = grid[row, column]
            pending = [(row, column)]
            seen.add((row, column))
            cells = []
            while pending:
                current_row, current_column = pending.pop()
                cells.append((current_row, current_column, grid[current_row, current_column]))
                for delta_row, delta_column in offsets:
                    neighbor = current_row + delta_row, current_column + delta_column
                    nr, nc = neighbor
                    if (
                        0 <= nr < grid.height and 0 <= nc < grid.width
                        and neighbor not in seen and grid[neighbor] != background
                        and (not monochrome or grid[neighbor] == color)
                    ):
                        seen.add(neighbor)
                        pending.append(neighbor)
            objects.append(GridObject(tuple(cells)))
    return tuple(objects)


def _content(obj: GridObject) -> tuple[tuple[int, int, int], ...]:
    top, left, _, _ = obj.bbox
    return tuple((row - top, column - left, color) for row, column, color in obj.cells)


def select_object(objects: tuple[GridObject, ...], criterion: str = "largest") -> GridObject:
    """Select by size, palette, extent, or uniqueness; ties use row-major cells.

    ``unique_shape`` compares translation-normalized occupancy (no rotation);
    ``unique_color`` compares entire palettes. Both require exactly one unique
    object and reject ambiguous inputs, rather than guessing the intended one.
    """
    if not objects:
        raise ValueError("Cannot select from an empty object collection")
    ordered = sorted(objects, key=lambda obj: obj.cells)
    if criterion == "unique_shape":
        shapes = Counter(obj.shape for obj in objects)
        unique = [obj for obj in ordered if shapes[obj.shape] == 1]
    elif criterion == "unique_content":
        contents = Counter(_content(obj) for obj in objects)
        unique = [obj for obj in ordered if contents[_content(obj)] == 1]
    elif criterion == "unique_color":
        palettes = Counter(obj.colors for obj in objects)
        unique = [obj for obj in ordered if palettes[obj.colors] == 1]
    else:
        scores = {
            "largest": lambda obj: -obj.size,
            "smallest": lambda obj: obj.size,
            "most_colors": lambda obj: -len(obj.colors),
            "least_colors": lambda obj: len(obj.colors),
            "widest": lambda obj: -obj.width,
            "tallest": lambda obj: -obj.height,
            "largest_bbox": lambda obj: -obj.height * obj.width,
            "smallest_bbox": lambda obj: obj.height * obj.width,
            "densest": lambda obj: -sum(color != 0 for _, _, color in obj.cells),
            "sparsest": lambda obj: sum(color != 0 for _, _, color in obj.cells),
        }
        if criterion not in scores:
            raise ValueError(f"Unknown object criterion: {criterion}")
        return min(ordered, key=scores[criterion])
    if len(unique) != 1:
        raise ValueError(f"{criterion} requires exactly one unique object")
    return unique[0]


def object_crop(obj: GridObject, background: int = 0) -> Grid:
    """Crop isolated object cells, filling unoccupied bounding-box cells."""
    top, left, bottom, right = obj.bbox
    cells = [[background] * (right - left) for _ in range(bottom - top)]
    for row, column, color in obj.cells:
        cells[row - top][column - left] = color
    return Grid(tuple(tuple(row) for row in cells))


def crop_bbox(grid: Grid, obj: GridObject) -> Grid:
    """Crop an object's bounding box, preserving all enclosed cells of the grid."""
    top, left, bottom, right = obj.bbox
    if bottom > grid.height or right > grid.width:
        raise ValueError("Object bounding box exceeds grid bounds")
    return Grid(tuple(row[left:right] for row in grid.cells[top:bottom]))


def extract_object(
    grid: Grid, criterion: str = "largest", background: int = 0,
    connectivity: int = 4, monochrome: bool = True, preserve_bbox: bool = False,
) -> Grid:
    """Select a component and crop it using the stated segmentation hypothesis."""
    obj = select_object(components(grid, background, connectivity, monochrome), criterion)
    return crop_bbox(grid, obj) if preserve_bbox else object_crop(obj, background)


def remove_small_objects(
    grid: Grid, max_size: int = 1, background: int = 0,
    connectivity: int = 4, monochrome: bool = True,
) -> Grid:
    """Erase foreground components containing at most ``max_size`` cells."""
    if max_size < 0:
        raise ValueError("Maximum size must be nonnegative")
    cells = [list(row) for row in grid.cells]
    for obj in components(grid, background, connectivity, monochrome):
        if obj.size <= max_size:
            for row, column, _ in obj.cells:
                cells[row][column] = background
    return Grid(tuple(tuple(row) for row in cells))


def fill_holes(grid: Grid, color: int, background: int = 0, connectivity: int = 4) -> Grid:
    """Fill background regions disconnected from the grid border.

    Connectivity governs background reachability; foreground need not be a
    single component or a single color. Existing foreground cells are retained.
    """
    offsets = _offsets(connectivity)
    exterior = {
        (row, column)
        for row in range(grid.height)
        for column in range(grid.width)
        if (row in (0, grid.height - 1) or column in (0, grid.width - 1))
        and grid[row, column] == background
    }
    pending = list(exterior)
    while pending:
        row, column = pending.pop()
        for delta_row, delta_column in offsets:
            neighbor = row + delta_row, column + delta_column
            nr, nc = neighbor
            if (
                0 <= nr < grid.height and 0 <= nc < grid.width
                and neighbor not in exterior and grid[neighbor] == background
            ):
                exterior.add(neighbor)
                pending.append(neighbor)
    return Grid(tuple(
        tuple(
            color if value == background and (row, column) not in exterior else value
            for column, value in enumerate(values)
        )
        for row, values in enumerate(grid.cells)
    ))


def complete_reflection(grid: Grid, axis: str = "vertical", background: int = 0) -> Grid:
    """Complete centered reflection orbits, rejecting conflicting colors.

    Vertical mirrors left/right, horizontal mirrors top/bottom. ``both`` closes
    both reflections, ``rotation`` the four quarter turns and ``full`` the whole
    dihedral orbit. Diagonal and rotational axes require square grids. Only
    background cells may change; a conflict raises ValueError without changing
    the input.
    """
    axes = {"vertical", "horizontal", "both", "main_diagonal", "anti_diagonal",
            "rotation", "full"}
    if axis not in axes:
        raise ValueError(f"Unknown reflection axis: {axis}")
    if axis not in {"vertical", "horizontal", "both"} and grid.height != grid.width:
        raise ValueError("This symmetry requires a square grid")
    side = grid.height
    cells = [list(row) for row in grid.cells]
    for row in range(grid.height):
        for column in range(grid.width):
            orbit = {(row, column)}
            if axis in {"vertical", "both"}:
                orbit.add((row, grid.width - column - 1))
            if axis in {"horizontal", "both"}:
                orbit.add((grid.height - row - 1, column))
            if axis == "both":
                orbit.add((grid.height - row - 1, grid.width - column - 1))
            if axis == "main_diagonal":
                orbit.add((column, row))
            if axis == "anti_diagonal":
                orbit.add((grid.height - column - 1, grid.width - row - 1))
            if axis in {"rotation", "full"}:
                orbit |= {(column, side - 1 - row), (side - 1 - row, side - 1 - column),
                          (side - 1 - column, row)}
            if axis == "full":
                orbit |= {(row, side - 1 - column), (side - 1 - row, column), (column, row),
                          (side - 1 - column, side - 1 - row)}
            colors = {grid[position] for position in orbit} - {background}
            if len(colors) > 1:
                raise ValueError("Conflicting foreground colors in reflection orbit")
            if colors:
                color = next(iter(colors))
                for target_row, target_column in orbit:
                    cells[target_row][target_column] = color
    return Grid(tuple(tuple(row) for row in cells))


def complete_bbox_reflection(grid: Grid, axis: str = "both", background: int = 0) -> Grid:
    """Complete a symmetry about the foreground bounding box instead of the grid center."""
    cells = [(r, c) for r, row in enumerate(grid.cells) for c, v in enumerate(row)
             if v != background]
    if not cells:
        raise ValueError("No foreground to complete")
    top = min(r for r, _ in cells)
    left = min(c for _, c in cells)
    bottom = max(r for r, _ in cells) + 1
    right = max(c for _, c in cells) + 1
    inner = Grid(tuple(row[left:right] for row in grid.cells[top:bottom]))
    done = complete_reflection(inner, axis, background)
    rows = [list(row) for row in grid.cells]
    for r, row in enumerate(done.cells):
        rows[top + r][left:right] = row
    return Grid(tuple(tuple(row) for row in rows))


def _runs(length: int, blocked: set[int]) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    start: int | None = None
    for index in range(length + 1):
        if index < length and index not in blocked:
            start = index if start is None else start
        elif start is not None:
            found.append((start, index))
            start = None
    return found


def _region(grid: Grid, top: int, left: int, bottom: int, right: int) -> GridObject:
    return GridObject(tuple((r, c, grid[r, c]) for r in range(top, bottom)
                            for c in range(left, right)))


def separator_cells(grid: Grid) -> list[list[GridObject]]:
    """Rectangular regions delimited by full lines of the most frequent line color.

    Regions keep all their cells, background included. The separator color is a
    hypothesis: the color with the most full rows and columns.
    """
    best: tuple[int, int] | None = None
    for color in range(1, 10):
        score = sum(set(row) == {color} for row in grid.cells) + sum(
            {grid[r, c] for r in range(grid.height)} == {color} for c in range(grid.width))
        if score and (best is None or score > best[0]):
            best = (score, color)
    if best is None:
        raise ValueError("No separator lines")
    color = best[1]
    row_lines = {r for r in range(grid.height) if set(grid.cells[r]) == {color}}
    column_lines = {c for c in range(grid.width)
                    if {grid[r, c] for r in range(grid.height)} == {color}}
    column_runs = _runs(grid.width, column_lines)
    return [[_region(grid, r0, c0, r1, c1) for c0, c1 in column_runs]
            for r0, r1 in _runs(grid.height, row_lines)]


def split_regions(grid: Grid, rows: int, columns: int) -> tuple[GridObject, ...]:
    """Equal rectangular regions in row-major order; sizes must divide evenly."""
    if grid.height % rows or grid.width % columns:
        raise ValueError("Grid does not split evenly")
    height, width = grid.height // rows, grid.width // columns
    return tuple(_region(grid, r * height, c * width, (r + 1) * height, (c + 1) * width)
                 for r in range(rows) for c in range(columns))
