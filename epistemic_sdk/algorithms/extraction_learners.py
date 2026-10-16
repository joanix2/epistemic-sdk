"""Learners for outputs extracted from the input: a crop, a window, or a color statistic."""
from collections import Counter
from collections.abc import Callable, Collection
from functools import partial

from . import grid_transforms as transforms
from .fitting import GridFunction, Training
from .grid_objects import Grid, components, dominant_color

ColorSelector = Callable[[Grid], Collection[int]]
ColorStatistic = Callable[[Grid], int]


def _fixed_color(grid: Grid, color: int) -> Collection[int]:
    return {color}


def _foreground_colors(grid: Grid) -> Collection[int]:
    return set(grid.colors) - {0}


def _color_selectors() -> dict[str, ColorSelector]:
    selectors: dict[str, ColorSelector] = {
        f"color_{color}": partial(_fixed_color, color=color) for color in range(1, 10)
    }
    selectors["nonzero"] = _foreground_colors
    selectors["least_common"] = lambda grid: {dominant_color(grid, least=True)}
    selectors["most_common"] = lambda grid: {dominant_color(grid)}
    return selectors


def _crop_by(grid: Grid, selector: ColorSelector, inset: int) -> Grid:
    return transforms.crop_to_colors(grid, selector(grid), inset)


def fit_crop(training: Training) -> GridFunction | None:
    """Output is the (inner) bounding box of a selected color of the input."""
    if any(t.height > s.height or t.width > s.width for s, t in training):
        return None
    for selector in _color_selectors().values():
        for inset in (0, 1):
            crop = partial(_crop_by, selector=selector, inset=inset)
            try:
                if all(crop(source) == target for source, target in training):
                    return crop
            except ValueError:
                continue
    return None


def _object_color(grid: Grid, largest: bool) -> int:
    objects = components(grid, 0, 4, True)
    if not objects:
        return 0
    pick = max if largest else min
    return pick(objects, key=lambda obj: (obj.size, obj.cells)).colors[0]


def _most_components_color(grid: Grid) -> int:
    counts = Counter(obj.colors[0] for obj in components(grid, 0, 4, True))
    if not counts:
        raise ValueError("no object")
    return counts.most_common(1)[0][0]


_STATISTICS: dict[str, ColorStatistic] = {
    "most_common_nonzero": dominant_color,
    "least_common_nonzero": partial(dominant_color, least=True),
    "most_common": partial(dominant_color, ignore_background=False),
    "largest_object_color": partial(_object_color, largest=True),
    "smallest_object_color": partial(_object_color, largest=False),
    "most_components_color": _most_components_color,
}


def _uniform(grid: Grid, statistic: ColorStatistic, shape: tuple[int, int] | None) -> Grid:
    color = statistic(grid)
    height, width = shape if shape is not None else (grid.height, grid.width)
    return Grid(tuple((color,) * width for _ in range(height)))


def fit_color_summary(training: Training) -> GridFunction | None:
    """Uniform output whose color is a statistic of the input; shape is fixed or inherited."""
    if any(len(t.colors) != 1 for _, t in training):
        return None
    shapes = {(t.height, t.width) for _, t in training}
    same_shape = all((s.height, s.width) == (t.height, t.width) for s, t in training)
    if len(shapes) != 1 and not same_shape:
        return None
    shape = next(iter(shapes)) if len(shapes) == 1 else None
    for statistic in _STATISTICS.values():
        try:
            if all(statistic(source) == target.colors[0] for source, target in training):
                return partial(_uniform, statistic=statistic, shape=shape)
        except ValueError:
            continue
    return None


_CORNERS = {
    "top_left": (False, False), "top_right": (False, True),
    "bottom_left": (True, False), "bottom_right": (True, True),
}


def _window(grid: Grid, height: int, width: int, bottom: bool, right: bool) -> Grid:
    if grid.height < height or grid.width < width:
        raise ValueError("grid smaller than the window")
    top = grid.height - height if bottom else 0
    left = grid.width - width if right else 0
    return Grid(tuple(row[left:left + width] for row in grid.cells[top:top + height]))


def fit_window(training: Training) -> GridFunction | None:
    """Output is a fixed-size window anchored at one corner of the input."""
    shapes = {(t.height, t.width) for _, t in training}
    if len(shapes) != 1:
        return None
    height, width = next(iter(shapes))
    if any(s.height < height or s.width < width or (s.height, s.width) == (height, width)
           for s, _ in training):
        return None
    for bottom, right in _CORNERS.values():
        window = partial(_window, height=height, width=width, bottom=bottom, right=right)
        if all(window(source) == target for source, target in training):
            return window
    return None
