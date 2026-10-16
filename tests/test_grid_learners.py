"""Task-fitted learners: exact fit on training pairs, honest refusal otherwise."""
import unittest

from epistemic_sdk.algorithms import grid_transforms as tf
from epistemic_sdk.algorithms.extraction_learners import fit_color_summary, fit_crop, fit_window
from epistemic_sdk.algorithms.fitted_families import FITTED_FAMILIES
from epistemic_sdk.algorithms.fitting import after
from epistemic_sdk.algorithms.grid_objects import Grid
from epistemic_sdk.algorithms.layout_learners import (
    fit_block_assembly,
    fit_block_reduction,
    fit_cell_expansion,
    fit_fractal,
    fit_partition_combination,
)
from epistemic_sdk.algorithms.local_rule import fit_local_rule
from tests.grid_helpers import grid


def fractal(source: Grid) -> Grid:
    blank = tf.blank(source.height, source.width)
    return tf.assemble([[source if value else blank for value in row] for row in source.cells])


def exactly_one_occupied(source: Grid) -> Grid:
    left, right = tf.half(source, "left"), tf.half(source, "right")
    return Grid(tuple(
        tuple(3 if (a != 0) != (b != 0) else 0 for a, b in zip(r1, r2, strict=True))
        for r1, r2 in zip(left.cells, right.cells, strict=True)
    ))


class LayoutLearnerTests(unittest.TestCase):
    def test_block_assembly_stacks_dihedral_images(self) -> None:
        training = [(grid("12 34"), grid("12 34 43 21")), (grid("56 78"), grid("56 78 87 65"))]
        function = fit_block_assembly(training)
        assert function is not None
        self.assertEqual(function(grid("19 28")), grid("19 28 82 91"))

    def test_block_assembly_rejects_unchanged_shape(self) -> None:
        self.assertIsNone(fit_block_assembly([(grid("12"), grid("12"))]))

    def test_fractal_places_the_input_where_cells_are_set(self) -> None:
        training = [(source, fractal(source)) for source in (grid("10 01"), grid("11 00"))]
        function = fit_fractal(training)
        assert function is not None
        self.assertEqual(function(grid("01 11")), fractal(grid("01 11")))

    def test_cell_expansion_requires_seen_colors(self) -> None:
        function = fit_cell_expansion([(grid("12"), grid("1122 1122"))])
        assert function is not None
        self.assertEqual(function(grid("21")), grid("2211 2211"))
        with self.assertRaises(ValueError):
            function(grid("13"))

    def test_partition_combination_is_a_lookup_on_occupancy(self) -> None:
        sources = [grid("1010 0110"), grid("0101 1001")]
        function = fit_partition_combination([(s, exactly_one_occupied(s)) for s in sources])
        assert function is not None
        unseen = grid("1100 0011")
        self.assertEqual(function(unseen), exactly_one_occupied(unseen))
        with self.assertRaises(ValueError):
            function(grid("123"))

    def test_partition_combination_refuses_single_support_keys(self) -> None:
        source = grid("1010 0110")
        self.assertIsNone(fit_partition_combination([(source, exactly_one_occupied(source))]))

    def test_block_reduction_by_equal_blocks(self) -> None:
        training = [(grid("1100 1100 0022 0022"), grid("10 02")),
                    (grid("3300 3300 0044 0044"), grid("30 04"))]
        function = fit_block_reduction(training)
        assert function is not None
        self.assertEqual(function(grid("5500 5500 0066 0066")), grid("50 06"))

    def test_block_reduction_by_separator_lines(self) -> None:
        function = fit_block_reduction([(grid("1151 1151 5555 2253 2253"), grid("11 23"))])
        assert function is not None
        self.assertEqual(function(grid("4454 4454 5555 6653 6653")), grid("44 63"))


class ExtractionLearnerTests(unittest.TestCase):
    def test_crop_selects_the_bounding_box_of_a_color(self) -> None:
        training = [(grid("1100 1100 0022 0002"), grid("22 02")),
                    (grid("0000 0220 3002 0000"), grid("220 002"))]
        function = fit_crop(training)
        assert function is not None
        self.assertEqual(function(grid("2000 0000 0011")), grid("2"))

    def test_color_summary_uses_a_color_statistic(self) -> None:
        training = [(grid("1123 4400"), grid("11")), (grid("5560 6600"), grid("66"))]
        function = fit_color_summary(training)
        assert function is not None
        self.assertEqual(function(grid("7700 7800")), grid("77"))

    def test_window_is_anchored_at_a_corner(self) -> None:
        training = [(grid("123 456 789"), grid("56 89")), (grid("111 121 345"), grid("21 45"))]
        function = fit_window(training)
        assert function is not None
        self.assertEqual(function(grid("987 654 321")), grid("54 21"))
        with self.assertRaises(ValueError):
            function(grid("1"))


class LocalRuleTests(unittest.TestCase):
    training = [(grid("1111 1001 1111 0000"), grid("1111 1441 1111 0000")),
                (grid("11100 10100 11100"), grid("11100 14100 11100"))]

    def test_enclosed_background_is_filled(self) -> None:
        function = fit_local_rule(self.training)
        assert function is not None
        self.assertEqual(function(grid("111 101 111 000")), grid("111 141 111 000"))

    def test_unseen_keys_leave_cells_unchanged(self) -> None:
        function = fit_local_rule(self.training)
        assert function is not None
        self.assertEqual(function(grid("23 00")), grid("23 00"))

    def test_refuses_shape_changes_and_identity(self) -> None:
        self.assertIsNone(fit_local_rule([(grid("11"), grid("1"))]))
        self.assertIsNone(fit_local_rule([(grid("12"), grid("12"))]))


class FittingTests(unittest.TestCase):
    def test_after_skips_when_the_prefix_changes_nothing(self) -> None:
        self.assertIsNone(after(tf.crop, fit_window)([(grid("11 11"), grid("11"))]))

    def test_after_fits_on_prefixed_inputs(self) -> None:
        training = [(grid("0000 0120 0000"), grid("1")), (grid("2000 0000 0003"), grid("2"))]
        function = after(tf.crop, fit_window)(training)
        assert function is not None
        self.assertEqual(function(grid("0050 0000")), grid("5"))

    def test_every_family_offers_cropped_variants(self) -> None:
        for learners in FITTED_FAMILIES.values():
            for name in [n for n in learners if not n.endswith("_cropped")]:
                self.assertIn(name + "_cropped", learners)


if __name__ == "__main__":
    unittest.main()
