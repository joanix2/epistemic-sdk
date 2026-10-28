"""Compact grid literals shared by tests: rows are digit strings split on whitespace."""
from epistemic_sdk.algorithms.grid_objects import Grid


def grid(text: str) -> Grid:
    return Grid(tuple(tuple(int(char) for char in row) for row in text.split()))
