"""Pure grid transforms added for the ARC taxonomy."""
import unittest

from epistemic_sdk.algorithms import grid_transforms as tf
from tests.grid_helpers import grid


class GridTransformTests(unittest.TestCase):
    def test_halves_drop_the_middle_line_of_odd_sizes(self) -> None:
        source = grid("123 456 789")
        self.assertEqual(tf.half(source, "top"), grid("123"))
        self.assertEqual(tf.half(source, "bottom"), grid("789"))
        self.assertEqual(tf.half(source, "left"), grid("1 4 7"))
        self.assertEqual(tf.half(source, "bottom_right"), grid("9"))

    def test_gravity_keeps_order_and_shift_drops_overflow(self) -> None:
        self.assertEqual(tf.gravity(grid("0102"), "left"), grid("1200"))
        self.assertEqual(tf.gravity(grid("1 0 2"), "down"), grid("0 1 2"))
        self.assertEqual(tf.shift(grid("123"), "right"), grid("012"))
        self.assertEqual(tf.shift(grid("1 2 3"), "up"), grid("2 3 0"))

    def test_concatenation_requires_matching_sizes(self) -> None:
        self.assertEqual(tf.hconcat(grid("12 34"), grid("5 6")), grid("125 346"))
        self.assertEqual(tf.vconcat(grid("12"), grid("34")), grid("12 34"))
        with self.assertRaises(ValueError):
            tf.hconcat(grid("1"), grid("1 2"))
        with self.assertRaises(ValueError):
            tf.vconcat(grid("1"), grid("12"))

    def test_boolean_logic_on_masks(self) -> None:
        a, b = grid("1102"), grid("1011")
        self.assertEqual(tf.logical_and(a, b), grid("1002"))
        self.assertEqual(tf.logical_or(a, b), grid("1112"))
        self.assertEqual(tf.logical_xor(a, b), grid("0110"))
        self.assertEqual(tf.logical_not(a), grid("0010"))
        with self.assertRaises(ValueError):
            tf.logical_and(a, grid("11"))

    def test_dilate_and_erode(self) -> None:
        dot = grid("000 020 000")
        self.assertEqual(tf.dilate(dot, 4), grid("020 222 020"))
        self.assertEqual(tf.dilate(dot, 8), grid("222 222 222"))
        self.assertEqual(tf.erode(grid("111 111 111"), 4), grid("000 010 000"))
        self.assertEqual(tf.erode(grid("111 111 111"), 8), grid("000 010 000"))
        self.assertEqual(tf.erode(dot, 4), grid("000 000 000"))


if __name__ == "__main__":
    unittest.main()
