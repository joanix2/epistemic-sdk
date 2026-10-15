"""The active epistemic loop: decide, select, observe, update.

The loop couples the belief distribution P(H) to the experimental policy P(E):
at each step a controller decides among three actions — *tester* (run a
discriminating experiment), *explorer* (gather corroborating data) and *abduire*
(invent new hypotheses) — the selector picks the experiment, and the Bayesian
updater revises P(H) from the outcome.
"""
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from epistemic_sdk import Hypothesis

from .bayesian_updater import BayesianUpdater, HypothesisDistribution
from .entropy_selector import EntropySelector


class Action(str, Enum):
    TESTER = "tester"
    EXPLORER = "explorer"
    ABDURE = "abduire"


class ActiveController:
    """Decide the next action of the active loop from the current P(H)."""

    def decide(
        self, hypotheses: Sequence[Hypothesis], distribution: HypothesisDistribution
    ) -> Action:
        survivors = [h for h in hypotheses if distribution.probability(h.id) > 0.0]
        if not survivors:
            return Action.ABDURE
        if len(survivors) == 1:
            return Action.EXPLORER
        return Action.TESTER


@dataclass(frozen=True)
class ActiveStep:
    action: Action
    experiment: Mapping[str, Any] | None
    output: Any | None
    distribution: HypothesisDistribution


@dataclass(frozen=True)
class ActiveTrace:
    steps: tuple[ActiveStep, ...]


class ActiveLoop:
    """Orchestrate the active loop: decide -> select -> observe -> update."""

    def __init__(
        self,
        controller: ActiveController,
        selector: EntropySelector,
        updater: BayesianUpdater,
        observe: Callable[[Mapping[str, Any]], Any],
    ) -> None:
        self._controller = controller
        self._selector = selector
        self._updater = updater
        self._observe = observe

    def run(
        self,
        hypotheses: Sequence[Hypothesis],
        candidates: Sequence[Mapping[str, Any]],
        *,
        max_steps: int = 20,
    ) -> ActiveTrace:
        distribution = HypothesisDistribution.uniform(hypotheses)
        remaining = list(candidates)
        steps: list[ActiveStep] = []

        for _ in range(max_steps):
            action = self._controller.decide(hypotheses, distribution)
            if action == Action.ABDURE:
                steps.append(ActiveStep(action, None, None, distribution))
                break
            if not remaining:
                steps.append(ActiveStep(action, None, None, distribution))
                break
            if action == Action.EXPLORER:
                chosen = remaining[0]
            else:
                chosen = self._selector.select(hypotheses, distribution, remaining)
            output = self._observe(chosen)
            distribution = self._updater.update(hypotheses, distribution, chosen, output)
            remaining.remove(chosen)
            steps.append(ActiveStep(action, chosen, output, distribution))

        return ActiveTrace(tuple(steps))
