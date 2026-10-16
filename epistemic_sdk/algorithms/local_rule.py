"""Learn a same-shape recoloring as a lookup on a per-cell descriptor.

Among descriptors that explain every training cell, the one needing the fewest
changed keys is kept (minimum description length); declaration order breaks ties.
A key maps to a constant color or, for relational descriptors, to a copied
neighbor/ray color. Unseen keys leave the cell unchanged, a prior checked only on
the training pairs. Every changed key needs two supporting cells so that a lookup
cannot merely memorize single cells.
"""
from collections.abc import Hashable
from functools import partial

from .fitting import GridFunction, Training
from .grid_features import DESCRIPTOR_ORDER, CellView, describe
from .grid_objects import Grid

_MIN_SUPPORT = 2

Occurrence = tuple[int, tuple[int, ...]]
Rule = tuple[str, int]  # ("const", color) or ("copy", candidate slot)
RuleTable = dict[Hashable, Rule]


def _resolve(occurrences: list[Occurrence]) -> Rule | None:
    """A constant if all outputs agree, else a candidate slot valid for every occurrence."""
    outputs = {output for output, _ in occurrences}
    if len(outputs) == 1:
        return "const", next(iter(outputs))
    slots = len(occurrences[0][1])
    for slot in range(slots):
        if all(len(cands) == slots and cands[slot] == output for output, cands in occurrences):
            return "copy", slot
    return None


def _changed_rules(name: str, training: Training) -> RuleTable | None:
    """Rules that change cells under descriptor ``name``; None if it cannot explain the data."""
    seen: dict[Hashable, list[Occurrence]] = {}
    colors: dict[Hashable, int] = {}
    for source, target in training:
        for r, line in enumerate(describe(source, name)):
            for c, cell in enumerate(line):
                seen.setdefault(cell.key, []).append((target[r, c], cell.candidates))
                colors[cell.key] = cell.color
    rules: RuleTable = {}
    for key, occurrences in seen.items():
        rule = _resolve(occurrences)
        if rule is None:
            return None
        if rule != ("const", colors[key]):
            if len(occurrences) < _MIN_SUPPORT:
                return None
            rules[key] = rule
    return rules or None


def _recolor(cell: CellView, rules: RuleTable) -> int:
    rule = rules.get(cell.key)
    if rule is None:
        return cell.color
    kind, value = rule
    if kind == "const":
        return value
    if cell.candidates[value] < 0:
        raise ValueError("copied cell is outside the grid")
    return cell.candidates[value]


def _apply(grid: Grid, name: str, rules: RuleTable) -> Grid:
    return Grid(tuple(
        tuple(_recolor(cell, rules) for cell in line) for line in describe(grid, name)
    ))


def fit_local_rule(training: Training) -> GridFunction | None:
    if any((s.height, s.width) != (t.height, t.width) for s, t in training):
        return None
    best: tuple[int, int, str, RuleTable] | None = None
    for order, name in enumerate(DESCRIPTOR_ORDER):
        rules = _changed_rules(name, training)
        if rules is not None and (best is None or (len(rules), order) < best[:2]):
            best = (len(rules), order, name, rules)
    if best is None:
        return None
    return partial(_apply, name=best[2], rules=best[3])
