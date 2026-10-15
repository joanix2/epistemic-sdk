"""Disagreement-based experiment selection (active learning).

The next experiment is the one whose outcome most splits the plausible
hypotheses. For each candidate input, every hypothesis is evaluated; the
candidate with the greatest number of distinct predictions wins. This is a proxy
for the expected mutual information ``E[I(H ; Y_e)]`` when hypotheses are
equally weighted over a finite domain.
"""
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from epistemic_sdk import Hypothesis, ProgramM1


def _distinct_count(values: Sequence[Any]) -> int:
    distinct: list[Any] = []
    for value in values:
        if not any(value == existing for existing in distinct):
            distinct.append(value)
    return len(distinct)


class DisagreementSelector:
    """Select the experiment whose outcome best discriminates the hypotheses."""

    def __init__(self, evaluate: Callable[[ProgramM1, Mapping[str, Any]], Any]) -> None:
        self._evaluate = evaluate

    def select(
        self,
        hypotheses: Sequence[Hypothesis],
        candidates: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        best = candidates[0]
        best_score = -1
        for candidate in candidates:
            predictions = [
                self._evaluate(hypothesis.program, candidate)
                for hypothesis in hypotheses
            ]
            score = _distinct_count(predictions)
            if score > best_score:
                best_score = score
                best = candidate
        return best
