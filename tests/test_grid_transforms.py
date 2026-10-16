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

    def test_blocks_round_trip_through_assemble(self) -> None:
        source = grid("1234 5678")
        blocks = [[tf.block(source, 0, column, 2, 2) for column in range(2)]]
        self.assertEqual(tf.assemble(blocks), source)
        self.assertEqual(tf.blank(1, 2), grid("00"))

    def test_crop_to_colors_with_inset(self) -> None:
        source = grid("00000 02220 02120 02220 00000")
        self.assertEqual(tf.crop_to_colors(source, {2}), grid("222 212 222"))
        self.assertEqual(tf.crop_to_colors(source, {2}, inset=1), grid("1"))
        with self.assertRaises(ValueError):
            tf.crop_to_colors(source, {2}, inset=2)
        with self.assertRaises(ValueError):
            tf.crop_to_colors(source, {7})


if __name__ == "__main__":
    unittest.main()
