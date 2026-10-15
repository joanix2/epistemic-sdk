"""ARC task loading and grid representation."""
import unittest

from examples.arc.loader import Grid


class Tests(unittest.TestCase):
    def test_grid_dimensions_and_access(self):
        grid = Grid(((0, 1), (2, 3), (4, 5)))
        self.assertEqual(grid.height, 3)
        self.assertEqual(grid.width, 2)
        self.assertEqual(grid[1, 0], 2)
        self.assertEqual(grid.colors, (0, 1, 2, 3, 4, 5))

    def test_grid_is_hashable(self):
        grid = Grid(((0, 1), (1, 0)))
        self.assertEqual(hash(grid), hash(Grid(((0, 1), (1, 0)))))


if __name__ == "__main__":
    unittest.main()
