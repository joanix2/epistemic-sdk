"""Cell descriptors are pure functions of the grid and independent of any task."""
import unittest

from epistemic_sdk.algorithms.grid_features import DESCRIPTOR_ORDER, OUTSIDE, describe
from tests.grid_helpers import grid


def descriptors(name: str, text: str) -> list[list[object]]:
    return [[cell.descriptor for cell in row] for row in describe(grid(text), name)]


class GridFeatureTests(unittest.TestCase):
    def test_every_declared_descriptor_is_computable(self) -> None:
        source = grid("0120 3004 0560")
        for name in DESCRIPTOR_ORDER:
            table = describe(source, name)
            self.assertEqual((len(table), len(table[0])), (3, 4))
            self.assertEqual([cell.color for cell in table[0]], [0, 1, 2, 0])
        self.assertEqual(len(set(DESCRIPTOR_ORDER)), len(DESCRIPTOR_ORDER))

    def test_enclosed_background_is_not_border_connected(self) -> None:
        table = descriptors("enclosed", "11100 10100 11100")
        self.assertTrue(table[1][1])
        self.assertFalse(table[1][3])

    def test_neighbor_counts_and_object_border(self) -> None:
        self.assertEqual(descriptors("neighbors_4_count", "010 111 010")[1][1], 4)
        border = descriptors("object_border", "1000 0220 0000")
        self.assertTrue(border[0][0])
        self.assertFalse(border[1][1])

    def test_relational_descriptors_expose_copy_candidates(self) -> None:
        cell = describe(grid("303"), "between")[0][1]
        self.assertEqual(cell.candidates[0], 3)
        outside = describe(grid("5"), "neighbor_copy")[0][0]
        self.assertEqual(outside.candidates, (OUTSIDE,) * 4)


if __name__ == "__main__":
    unittest.main()
