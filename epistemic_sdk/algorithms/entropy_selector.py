"""Entropy-based experiment selection, weighted by P(H).

For deterministic hypotheses, the expected information gain of an experiment is
the entropy of the predicted output distribution (weighted by P(H)); selecting
the maximum-entropy experiment therefore maximizes ``I(H ; Y_e)``. Unlike the
unweighted disagreement selector, this one re-weights each experiment by how
much probability mass still sits on the hypotheses it can discriminate.
"""
import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from epistemic_sdk import Hypothesis, ProgramM1

from .bayesian_updater import HypothesisDistribution


def _weighted_groups(
    predictions: Sequence[Any], weights: Sequence[float]
) -> list[float]:
    group_values: list[Any] = []
    group_weights: list[float] = []
    for prediction, weight in zip(predictions, weights, strict=True):
        for index, value in enumerate(group_values):
            if value == prediction:
                group_weights[index] += weight
                break
        else:
            group_values.append(prediction)
            group_weights.append(weight)
    return group_weights


class EntropySelector:
    """Select the experiment maximizing the entropy of predicted outputs, weighted by P(H)."""

    def __init__(self, evaluate: Callable[[ProgramM1, Mapping[str, Any]], Any]) -> None:
        self._evaluate = evaluate

    def select(
        self,
        hypotheses: Sequence[Hypothesis],
        distribution: HypothesisDistribution,
        candidates: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        best = candidates[0]
        best_entropy = -1.0
        for candidate in candidates:
            predictions = [self._evaluate(h.program, candidate) for h in hypotheses]
            weights = [distribution.probability(h.id) for h in hypotheses]
            groups = _weighted_groups(predictions, weights)
            entropy = -sum(w * math.log(w) for w in groups if w > 0.0)
            if entropy > best_entropy:
                best_entropy = entropy
                best = candidate
        return best
