"""Experiment selection: choose the next observation to seek (active learning)."""
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from epistemic_sdk.m1.hypothesis import Hypothesis


class ExperimentSelector(Protocol):
    """Select the next experiment that best discriminates the hypotheses.

    The loop is active when this port — not a passive sensor — decides which
    observation to seek next. A counter-example then reconfigures the
    experimental policy rather than merely lowering a hypothesis's probability.
    """

    def select(
        self,
        hypotheses: Sequence[Hypothesis],
        candidates: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        """Return the candidate input whose observation best discriminates."""
        ...
