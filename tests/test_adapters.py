"""Tests for the Phase 3 optional adapters (MLP, Popper)."""
import importlib.util
import unittest

from epistemic_sdk.algorithms.mlp import MLPFunction
from epistemic_sdk.algorithms.popper_ilp import PopperILPEngine

_HAS_SKLEARN = importlib.util.find_spec("sklearn") is not None


class MLPTests(unittest.TestCase):
    @unittest.skipUnless(_HAS_SKLEARN, "scikit-learn not installed")
    def test_mlp_learns_function(self):
        cases = [
            ({"A": a, "B": b}, a + b)
            for a in (0.0, 0.25, 0.5, 0.75, 1.0)
            for b in (0.0, 0.25, 0.5, 0.75, 1.0)
        ]
        model = MLPFunction(
            ("A", "B"), hidden_layer_sizes=(32, 32), max_iter=5000, random_state=0
        )
        model.fit(cases)
        for inputs, expected in cases:
            self.assertAlmostEqual(model.predict(inputs), expected, delta=0.2)

    @unittest.skipUnless(_HAS_SKLEARN, "scikit-learn not installed")
    def test_mlp_missing_feature_raises(self):
        model = MLPFunction(("A", "B"))
        with self.assertRaises(KeyError):
            model.predict({"A": 1.0})  # "B" is missing


class PopperTests(unittest.TestCase):
    def test_popper_requires_dependency(self):
        # Popper is not installed in this environment: the lazy import must fail cleanly.
        with self.assertRaises(ImportError):
            PopperILPEngine()


if __name__ == "__main__":
    unittest.main()
