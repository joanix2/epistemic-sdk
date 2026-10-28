"""Semantic checks for reusable grid object hypotheses."""

import unittest

from epistemic_sdk.algorithms.grid_objects import (
    Grid,
    GridObject,
    complete_bbox_reflection,
    complete_reflection,
    components,
    crop_bbox,
    extract_object,
    fill_holes,
    object_crop,
    remove_small_objects,
    select_object,
    separator_cells,
    split_regions,
)
from tests.grid_helpers import grid as parse


class GridObjectTests(unittest.TestCase):
    def test_grid_value_and_rectangularity(self) -> None:
        grid = Grid(((2, 1), (0, 2)))
        self.assertEqual((grid.height, grid.width, grid.colors), (2, 2, (0, 1, 2)))
        self.assertEqual(grid[0, 1], 1)
        self.assertEqual(hash(grid), hash(Grid(((2, 1), (0, 2)))))
        with self.assertRaises(ValueError):
            Grid(((1,), (2, 3)))
        self.assertEqual(components(Grid(())), ())

    def test_connectivity_and_monochrome_are_independent(self) -> None:
        grid = Grid(((1, 2, 0), (0, 0, 2)))
        self.assertEqual([obj.size for obj in components(grid)], [1, 1, 1])
        self.assertEqual([obj.size for obj in components(grid, connectivity=8)], [1, 2])
        self.assertEqual([obj.size for obj in components(grid, monochrome=False)], [2, 1])
        joined = components(grid, connectivity=8, monochrome=False)
        self.assertEqual(len(joined), 1)
        self.assertEqual(joined[0].colors, (1, 2))

    def test_background_is_explicit(self) -> None:
        grid = Grid(((9, 0, 9), (9, 0, 2)))
        objects = components(grid, background=9)
        self.assertEqual([obj.size for obj in objects], [2, 1])
        self.assertEqual(objects[0].colors, (0,))
        self.assertEqual(extract_object(grid, background=9), Grid(((0,), (0,))))
        with self.assertRaises(ValueError):
            components(grid, connectivity=6)

    def test_object_value_bbox_and_shape(self) -> None:
        obj = GridObject(((3, 4, 7), (2, 3, 8), (3, 3, 7)))
        self.assertEqual(obj.cells[0], (2, 3, 8))
        self.assertEqual(obj.bbox, (2, 3, 4, 5))
        self.assertEqual((obj.height, obj.width, obj.size), (2, 2, 3))
        self.assertEqual(obj.shape, ((0, 0), (1, 0), (1, 1)))
        for cells in ((), ((-1, 0, 1),), ((0, 0, 1), (0, 0, 2))):
            with self.assertRaises(ValueError):
                GridObject(cells)

    def test_crop_distinguishes_enclosed_foreground(self) -> None:
        grid = Grid(((1, 1, 1), (1, 2, 1), (1, 1, 1)))
        obj = select_object(components(grid))
        self.assertEqual(object_crop(obj), Grid(((1, 1, 1), (1, 0, 1), (1, 1, 1))))
        self.assertEqual(crop_bbox(grid, obj), grid)
        self.assertEqual(extract_object(grid, preserve_bbox=True), grid)
        with self.assertRaises(ValueError):
            crop_bbox(grid, GridObject(((3, 0, 1),)))

    def test_deterministic_ties_ignore_input_object_order(self) -> None:
        objects = components(Grid(((1, 0, 2),)))
        self.assertEqual(select_object(objects), objects[0])
        self.assertEqual(select_object(tuple(reversed(objects))), objects[0])
        with self.assertRaises(ValueError):
            select_object(())
        with self.assertRaises(ValueError):
            select_object(objects, "unrecognized")

    def test_unique_shape_and_color_are_not_first_match(self) -> None:
        grid = Grid(((1, 0, 1, 0, 2), (0, 0, 0, 0, 2)))
        objects = components(grid)
        self.assertEqual(select_object(objects, "unique_shape"), objects[2])
        self.assertEqual(select_object(objects, "unique_color"), objects[2])
        with self.assertRaises(ValueError):
            select_object(objects[:2], "unique_shape")
        with self.assertRaises(ValueError):
            select_object((objects[0], objects[2]), "unique_color")

    def test_palette_and_extent_selection(self) -> None:
        objects = components(Grid(((1, 2, 0, 3), (0, 0, 0, 3))), monochrome=False)
        self.assertEqual(select_object(objects, "most_colors"), objects[0])
        self.assertEqual(select_object(objects, "least_colors"), objects[1])
        self.assertEqual(select_object(objects, "widest"), objects[0])
        self.assertEqual(select_object(objects, "tallest"), objects[1])

    def test_remove_noise_and_preserve_input(self) -> None:
        grid = Grid(((1, 1, 0, 2), (0, 0, 0, 0)))
        self.assertEqual(remove_small_objects(grid), Grid(((1, 1, 0, 0), (0, 0, 0, 0))))
        self.assertEqual(grid[0, 3], 2)
        self.assertEqual(remove_small_objects(grid, max_size=0), grid)
        with self.assertRaises(ValueError):
            remove_small_objects(grid, max_size=-1)

    def test_holes_do_not_fill_border_connected_background(self) -> None:
        grid = Grid(((0, 1, 1, 1), (0, 1, 0, 1), (0, 1, 1, 1)))
        self.assertEqual(fill_holes(grid, 8), Grid(((0, 1, 1, 1), (0, 1, 8, 1), (0, 1, 1, 1))))
        diagonal = Grid(((0, 1, 1), (1, 0, 1), (1, 1, 1)))
        self.assertEqual(fill_holes(diagonal, 8)[1, 1], 8)
        self.assertEqual(fill_holes(diagonal, 8, connectivity=8), diagonal)
        self.assertEqual(fill_holes(Grid(()), 1), Grid(()))

    def test_reflections_preserve_existing_foreground(self) -> None:
        grid = Grid(((2, 0, 0), (0, 0, 0)))
        self.assertEqual(complete_reflection(grid), Grid(((2, 0, 2), (0, 0, 0))))
        self.assertEqual(complete_reflection(grid, "horizontal"), Grid(((2, 0, 0), (2, 0, 0))))
        both = complete_reflection(grid, "both")
        self.assertEqual(both, Grid(((2, 0, 2), (2, 0, 2))))
        self.assertEqual(complete_reflection(both, "both"), both)
        self.assertEqual(grid, Grid(((2, 0, 0), (0, 0, 0))))

    def test_reflections_reject_conflicts_without_overwriting(self) -> None:
        grid = Grid(((1, 0), (0, 2)))
        with self.assertRaises(ValueError):
            complete_reflection(grid, "both")
        self.assertEqual(grid, Grid(((1, 0), (0, 2))))
        with self.assertRaises(ValueError):
            complete_reflection(Grid(((1, 2),)))

    def test_diagonal_reflections_and_invalid_axis(self) -> None:
        grid = Grid(((0, 3), (0, 0)))
        self.assertEqual(complete_reflection(grid, "main_diagonal"), Grid(((0, 3), (3, 0))))
        grid = Grid(((3, 0), (0, 0)))
        self.assertEqual(complete_reflection(grid, "anti_diagonal"), Grid(((3, 0), (0, 3))))
        with self.assertRaises(ValueError):
            complete_reflection(Grid(((1, 0),)), "main_diagonal")
        with self.assertRaises(ValueError):
            complete_reflection(grid, "other")

    def test_rotation_and_full_orbits(self) -> None:
        self.assertEqual(complete_reflection(parse("100 000 000"), "rotation"),
                         parse("101 000 101"))
        self.assertEqual(complete_reflection(parse("120 000 000"), "full"),
                         parse("121 202 121"))

    def test_bbox_reflection_uses_the_foreground_box(self) -> None:
        self.assertEqual(complete_bbox_reflection(parse("0000 0110 0200"), "vertical"),
                         parse("0000 0110 0220"))
        with self.assertRaises(ValueError):
            complete_bbox_reflection(parse("000"), "vertical")

    def test_separator_cells_and_equal_splits(self) -> None:
        regions = separator_cells(parse("1151 1151 5555 2253 2253"))
        self.assertEqual([[object_crop(region) for region in row] for row in regions],
                         [[parse("11 11"), parse("1 1")], [parse("22 22"), parse("3 3")]])
        with self.assertRaises(ValueError):
            separator_cells(parse("12 21"))
        halves = split_regions(parse("1122"), 1, 2)
        self.assertEqual([object_crop(region) for region in halves], [parse("11"), parse("22")])
        with self.assertRaises(ValueError):
            split_regions(parse("1122"), 1, 3)


if __name__ == "__main__":
    unittest.main()
