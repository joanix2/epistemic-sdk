"""Shared vocabulary for learners that estimate a grid function from training pairs.

A learner returns a pure ``Grid -> Grid`` callable that reproduces every training
pair, or ``None``. Exact reproduction is evidence of fit on the observed pairs,
not proof that the rule holds elsewhere. Inapplicable inputs raise ``ValueError``,
which the evaluator interprets as "undefined".
"""
from collections.abc import Callable, Sequence

from .grid_objects import Grid

Training = Sequence[tuple[Grid, Grid]]
GridFunction = Callable[[Grid], Grid]
Learner = Callable[[Training], GridFunction | None]


def after(prefix: GridFunction, learner: Learner) -> Learner:
    """Fit ``learner`` on inputs transformed by ``prefix``; skipped if it changes nothing."""
    def fit(training: Training) -> GridFunction | None:
        prepared = [(prefix(source), target) for source, target in training]
        if all(new == old for (new, _), (old, _) in zip(prepared, training, strict=True)):
            return None
        function = learner(prepared)
        if function is None:
            return None

        def apply(grid: Grid) -> Grid:
            return function(prefix(grid))

        return apply

    return fit
