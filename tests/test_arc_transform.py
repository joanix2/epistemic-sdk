"""Grid transformations and recolor discovery."""
import unittest

from examples.arc.loader import Example, Grid
from examples.arc.transformations import (
    discover_recolor,
    flip_horizontal,
    flip_vertical,
    recolor,
)


class Tests(unittest.TestCase):
    def test_flip(self):
        grid = Grid(((1, 2), (3, 4)))
        self.assertEqual(flip_horizontal(grid), Grid(((2, 1), (4, 3))))
        self.assertEqual(flip_vertical(grid), Grid(((3, 4), (1, 2))))

    def test_discover_recolor(self):
        examples = (
            Example(Grid(((0, 4), (4, 0))), Grid(((0, 1), (1, 0)))),
            Example(Grid(((4, 4), (0, 4))), Grid(((1, 1), (0, 1)))),
        )
        mapping = discover_recolor(examples)
        self.assertEqual(mapping, {4: 1})

    def test_recolor_applies_mapping(self):
        grid = Grid(((0, 4), (4, 0)))
        self.assertEqual(recolor(grid, {4: 1}), Grid(((0, 1), (1, 0))))


if __name__ == "__main__":
    unittest.main()
