"""Bayesian update of hypothesis probabilities P(H | D).

For deterministic hypotheses over a finite domain, the likelihood of an
observation (inputs -> output) is 1 when the hypothesis predicts ``output`` and
0 otherwise. Bayes therefore refutes the incompatible hypotheses and
renormalizes the compatible ones. When every hypothesis is refuted, the
posterior has zero total mass — the signal to *abduce* (expand the hypothesis
space), not to keep testing the same models.
"""
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from epistemic_sdk import Hypothesis, ProgramM1


@dataclass(frozen=True)
class HypothesisDistribution:
    """P(H): a probability distribution over hypotheses, keyed by hypothesis id."""

    weights: tuple[tuple[str, float], ...] = ()

    def probability(self, hypothesis_id: str) -> float:
        return dict(self.weights).get(hypothesis_id, 0.0)

    @classmethod
    def uniform(cls, hypotheses: Sequence[Hypothesis]) -> "HypothesisDistribution":
        if not hypotheses:
            return cls()
        return cls(tuple((h.id, 1.0 / len(hypotheses)) for h in hypotheses))


class BayesianUpdater:
    """Update P(H | D) via Bayes with deterministic likelihoods."""

    def __init__(self, evaluate: Callable[[ProgramM1, Mapping[str, Any]], Any]) -> None:
        self._evaluate = evaluate

    def update(
        self,
        hypotheses: Sequence[Hypothesis],
        prior: HypothesisDistribution,
        inputs: Mapping[str, Any],
        output: Any,
    ) -> HypothesisDistribution:
        posterior = [
            (h.id, prior.probability(h.id) * self._likelihood(h, inputs, output))
            for h in hypotheses
        ]
        total = sum(weight for _, weight in posterior)
        if total <= 0.0:
            return HypothesisDistribution()
        return HypothesisDistribution(
            tuple((hypothesis_id, weight / total) for hypothesis_id, weight in posterior)
        )

    def _likelihood(
        self, hypothesis: Hypothesis, inputs: Mapping[str, Any], output: Any
    ) -> float:
        predicted = self._evaluate(hypothesis.program, inputs)
        return 1.0 if predicted == output else 0.0
