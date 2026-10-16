"""ARC grid-transformation discovery reusing the generalized language-discovery loop.

This module adapts the SDK's ``LanguageDiscovery`` machinery to ARC tasks: it
enumerates compositions of elementary grid transformations (a ``LanguageM2`` of
unary operators over the ``Grid`` sort), keeps the programs consistent with a
task's training examples, and corroborates them against the held-out test
example. The discovered program is classified by its transformation family.

Nothing here hardcodes a task id or an expected answer; the grammar, evaluator
and family table are derived from the elementary transformations in
``examples.arc.transformations``.
"""
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from epistemic_sdk import LanguageM2, Operator, Sort
from epistemic_sdk.algorithms.language_discovery import LanguageDiscovery
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

from . import transformations as tf
from .loader import Grid, Task

GRID = "Grid"

OPERATOR_FAMILY: dict[str, str] = {
    "recolor": "recolor",
    "flip_horizontal": "flip",
    "flip_vertical": "flip",
    "rotate_90": "rotation",
    "rotate_180": "rotation",
    "rotate_270": "rotation",
    "transpose": "diagonal",
    "anti_transpose": "diagonal",
    "crop": "crop",
    "upscale_2": "scale",
    "upscale_3": "scale",
    "pad_square": "padding",
}

MAX_CELLS = 2048

# Neutral probe grids added to the semantic-equivalence domain so that distinct
# operators which coincide on a task's (few) training inputs are not collapsed
# into one representative. They are used for de-duplication only, never for
# consistency checking, so they introduce no train/test leakage.
PROBE_GRIDS: tuple[Grid, ...] = (
    Grid(((1, 2), (3, 4))),
    Grid(((1, 2, 3), (4, 5, 6))),
    Grid(((0, 0, 0), (0, 7, 0), (0, 0, 0))),
    Grid(((0, 0), (0, 0))),
)


class _Undefined:
    """Sentinel for evaluation errors and oversized grids (never equals a ``Grid``)."""

    def __repr__(self) -> str:
        return "UNDEFINED"


UNDEFINED = _Undefined()

Evaluator = Callable[[Term, Mapping[str, Any]], Any]


@dataclass(frozen=True)
class TaskDiscovery:
    task_id: str
    program: Term | None
    language: LanguageM2
    solved: bool
    family: str | None
    families_used: tuple[str, ...]


def transformation_language() -> LanguageM2:
    return LanguageM2(
        id="arc_grid",
        version="1.0.0",
        sorts=(Sort(GRID),),
        operators=tuple(Operator(name, (GRID,), GRID) for name in OPERATOR_FAMILY),
    )


def make_evaluate(recolor_mapping: Mapping[int, int], *, max_cells: int = MAX_CELLS) -> Evaluator:
    dispatch: dict[str, Callable[[Grid], Grid]] = {
        "recolor": lambda grid: tf.recolor(grid, recolor_mapping),
        "flip_horizontal": tf.flip_horizontal,
        "flip_vertical": tf.flip_vertical,
        "rotate_90": tf.rotate_90,
        "rotate_180": tf.rotate_180,
        "rotate_270": tf.rotate_270,
        "transpose": tf.transpose,
        "anti_transpose": tf.anti_transpose,
        "crop": tf.crop,
        "upscale_2": lambda grid: tf.upscale(grid, 2),
        "upscale_3": lambda grid: tf.upscale(grid, 3),
        "pad_square": tf.pad_square,
    }

    def evaluate(term: Term, inputs: Mapping[str, Any]) -> Any:
        if isinstance(term, Variable):
            value = inputs.get(term.name)
            return value if isinstance(value, Grid) else UNDEFINED
        if isinstance(term, Application):
            function = dispatch.get(term.operator)
            if function is None or len(term.arguments) != 1:
                return UNDEFINED
            argument = evaluate(term.arguments[0], inputs)
            if not isinstance(argument, Grid):
                return UNDEFINED
            try:
                result = function(argument)
            except Exception:
                return UNDEFINED
            if result.height * result.width > max_cells:
                return UNDEFINED
            return result
        return UNDEFINED

    return evaluate


def _operator_names(term: Term) -> tuple[str, ...]:
    if isinstance(term, Application):
        return (term.operator,) + tuple(
            name for argument in term.arguments for name in _operator_names(argument)
        )
    return ()


def _families_used(program: Term | None) -> tuple[str, ...]:
    if program is None:
        return ()
    names = _operator_names(program)
    return tuple(sorted({OPERATOR_FAMILY[name] for name in names if name in OPERATOR_FAMILY}))


def _classify_family(program: Term | None) -> str | None:
    if program is None:
        return None
    if isinstance(program, Variable):
        return "identity"
    if (
        isinstance(program, Application)
        and len(program.arguments) == 1
        and isinstance(program.arguments[0], Variable)
        and program.arguments[0].name == "g"
        and program.operator in OPERATOR_FAMILY
    ):
        return OPERATOR_FAMILY[program.operator]
    return "composition"


def discover_task(task: Task, *, max_nodes: int = 4, max_cells: int = MAX_CELLS) -> TaskDiscovery:
    language = transformation_language()
    if not task.train:
        return TaskDiscovery(task.id, None, language, False, None, ())
    if not task.test:
        return TaskDiscovery(task.id, None, language, False, None, ())

    mapping: dict[int, int] = {}
    if all(
        example.input.height == example.output.height
        and example.input.width == example.output.width
        for example in task.train
    ):
        try:
            mapping = tf.discover_recolor(task.train)
        except ValueError:
            mapping = {}

    evaluate = make_evaluate(mapping, max_cells=max_cells)
    training = [({"g": example.input}, example.output) for example in task.train]
    probes = [example.input for example in task.train]
    probes.extend(PROBE_GRIDS)
    domain = tuple(dict.fromkeys(probes))

    discovery = LanguageDiscovery(
        language, ("g",), evaluate, domain, max_nodes=max_nodes
    )
    result = discovery.fit(training)

    program = result.program
    solved = program is not None and all(
        evaluate(program, {"g": example.input}) == example.output
        for example in task.test
    )

    families_used = _families_used(program)
    family = _classify_family(program)
    return TaskDiscovery(task.id, program, language, solved, family, families_used)
