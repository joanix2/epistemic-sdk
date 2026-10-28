"""Grid transformations and recolor discovery."""
import unittest

from examples.arc.loader import Example, Grid
from examples.arc.transformations import (
    anti_transpose,
    crop,
    discover_recolor,
    flip_horizontal,
    flip_vertical,
    pad_square,
    recolor,
    rotate_90,
    rotate_180,
    rotate_270,
    transpose,
    upscale,
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


class TransformTests(unittest.TestCase):
    def test_rotate_90(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(rotate_90(grid), Grid(((4, 1), (5, 2), (6, 3))))

    def test_rotate_180(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(rotate_180(grid), Grid(((6, 5, 4), (3, 2, 1))))

    def test_rotate_270(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(rotate_270(grid), Grid(((3, 6), (2, 5), (1, 4))))

    def test_transpose(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(transpose(grid), Grid(((1, 4), (2, 5), (3, 6))))

    def test_anti_transpose(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(anti_transpose(grid), Grid(((6, 3), (5, 2), (4, 1))))

    def test_rotate_90_four_times_is_identity(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        rotated = rotate_90(rotate_90(rotate_90(rotate_90(grid))))
        self.assertEqual(rotated, grid)

    def test_crop_bounding_box(self):
        grid = Grid(((0, 0, 0, 0), (0, 5, 0, 0), (0, 0, 7, 0), (0, 0, 0, 0)))
        self.assertEqual(crop(grid), Grid(((5, 0), (0, 7))))

    def test_crop_all_background_is_noop(self):
        grid = Grid(((0, 0), (0, 0)))
        self.assertEqual(crop(grid), grid)

    def test_upscale_factor_two(self):
        grid = Grid(((1, 2), (3, 4)))
        self.assertEqual(
            upscale(grid, 2),
            Grid(((1, 1, 2, 2), (1, 1, 2, 2), (3, 3, 4, 4), (3, 3, 4, 4))),
        )

    def test_upscale_factor_one_returns_equal_grid(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(upscale(grid, 1), grid)

    def test_upscale_factor_zero_raises(self):
        grid = Grid(((1, 2), (3, 4)))
        with self.assertRaises(ValueError):
            upscale(grid, 0)

    def test_pad_square_adds_bottom_row(self):
        grid = Grid(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(pad_square(grid), Grid(((1, 2, 3), (4, 5, 6), (0, 0, 0))))

    def test_pad_square_square_grid_is_noop(self):
        grid = Grid(((1, 2), (3, 4)))
        self.assertEqual(pad_square(grid), grid)


if __name__ == "__main__":
    unittest.main()
