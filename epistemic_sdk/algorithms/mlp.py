"""MLP function learner: a non-symbolic alternative (scikit-learn MLPRegressor).

Optional dependency: ``scikit-learn`` (declared in the ``mlp`` extra). Imported
lazily and dynamically, so ``epistemic_sdk`` stays importable without it.

This is deliberately **not** an ``InferenceEngine``: an MLP produces an opaque
continuous function, not a declarative ``ProgramM1``. It demonstrates the
boundary between the SDK's symbolic discovery (explanations as programs) and
non-symbolic function approximation (a black box).
"""

import importlib
from collections.abc import Mapping, Sequence
from typing import Any

# One training case: variable bindings -> expected (continuous) output.
Case = tuple[Mapping[str, Any], float]


class MLPFunction:
    """A fitted neural function over a fixed, ordered set of input features."""

    def __init__(
        self,
        feature_names: tuple[str, ...],
        *,
        hidden_layer_sizes: tuple[int, ...] = (8,),
        max_iter: int = 2000,
        random_state: int = 0,
    ) -> None:
        self._feature_names = feature_names
        self._model: Any = self._build(hidden_layer_sizes, max_iter, random_state)

    @staticmethod
    def _build(
        hidden_layer_sizes: tuple[int, ...], max_iter: int, random_state: int
    ) -> Any:
        try:
            neural_network = importlib.import_module("sklearn.neural_network")
        except ImportError as exc:
            raise ImportError(
                "MLPFunction requires the optional dependency 'scikit-learn' "
                "(install with: pip install 'epistemic-sdk[mlp]')"
            ) from exc
        return neural_network.MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
            random_state=random_state,
        )

    def _feature_row(self, inputs: Mapping[str, Any]) -> list[float]:
        return [float(inputs[name]) for name in self._feature_names]

    def fit(self, cases: Sequence[Case]) -> "MLPFunction":
        """Train on ``(inputs, expected_output)`` cases and return ``self``."""
        features = [self._feature_row(inputs) for inputs, _output in cases]
        targets = [float(output) for _inputs, output in cases]
        self._model.fit(features, targets)
        return self

    def predict(self, inputs: Mapping[str, Any]) -> float:
        """Return the learned function's output for ``inputs``."""
        return float(self._model.predict([self._feature_row(inputs)])[0])
