"""Tests for ARC grid-transformation discovery using LanguageDiscovery."""
import os
import unittest
from pathlib import Path

from examples.arc.discovery import (
    GRID,
    discover_task,
    transformation_language,
)
from examples.arc.loader import Example, Grid, Task

ARC_DATA = Path(
    os.environ.get("ARC_DATA_DIR", "/home/joan/Documents/Programation/ARC-AGI/data/training")
)


class UnitDiscoveryTests(unittest.TestCase):
    def test_transformation_language_has_unary_operators(self):
        language = transformation_language()
        self.assertEqual(language.id, "arc_grid")
        self.assertEqual(language.version, "1.0.0")
        for op in language.operators:
            self.assertEqual(op.arguments, (GRID,))
            self.assertEqual(op.result, GRID)
        names = {op.name for op in language.operators}
        for expected in (
            "rotate_180",
            "flip_horizontal",
            "recolor",
            "crop",
            "upscale_2",
            "pad_square",
        ):
            self.assertIn(expected, names)

    def test_discovers_rotate_180(self):
        train = (
            Example(
                Grid(((0, 0, 1), (0, 0, 2), (0, 0, 0))),
                Grid(((0, 0, 0), (2, 0, 0), (1, 0, 0))),
            ),
            Example(Grid(((1, 2), (3, 4))), Grid(((4, 3), (2, 1)))),
        )
        test = (Example(Grid(((5, 6), (7, 8))), Grid(((8, 7), (6, 5)))),)
        disc = discover_task(Task(id="test_rotate180", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("rotation", "composition"))

    def test_discovers_flip_horizontal(self):
        # A second example distinguishes reflection from a fitted color permutation.
        train = (
            Example(Grid(((1, 2, 3), (4, 5, 6))), Grid(((3, 2, 1), (6, 5, 4)))),
            Example(Grid(((1, 3, 2), (6, 4, 5))), Grid(((2, 3, 1), (5, 4, 6)))),
        )
        test = (Example(Grid(((7, 8), (9, 0))), Grid(((8, 7), (0, 9)))),)
        disc = discover_task(Task(id="test_flip_h", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("flip", "composition"))

    def test_discovers_transpose(self):
        train = (Example(Grid(((1, 2, 3), (4, 5, 6))), Grid(((1, 4), (2, 5), (3, 6)))),)
        test = (Example(Grid(((7, 8), (9, 0))), Grid(((7, 9), (8, 0)))),)
        disc = discover_task(Task(id="test_transpose", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("diagonal", "composition"))

    def test_discovers_crop(self):
        train = (Example(Grid(((0, 0, 0), (0, 1, 2), (0, 0, 0))), Grid(((1, 2),))),)
        test = (Example(Grid(((0, 0, 0), (0, 3, 4), (0, 0, 0))), Grid(((3, 4),))),)
        disc = discover_task(Task(id="test_crop", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("crop", "composition"))

    def test_discovers_recolor(self):
        train = (
            Example(Grid(((0, 4), (4, 0))), Grid(((0, 1), (1, 0)))),
            Example(Grid(((4, 4), (0, 4))), Grid(((1, 1), (0, 1)))),
        )
        test = (Example(Grid(((0, 4), (4, 4))), Grid(((0, 1), (1, 1)))),)
        disc = discover_task(Task(id="test_recolor", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("recolor", "composition"))

    def test_discovers_padding(self):
        train = (
            Example(Grid(((1, 2, 3), (4, 5, 6))), Grid(((1, 2, 3), (4, 5, 6), (0, 0, 0)))),
        )
        test = (
            Example(Grid(((7, 8, 9), (1, 2, 3))), Grid(((7, 8, 9), (1, 2, 3), (0, 0, 0)))),
        )
        disc = discover_task(Task(id="test_pad", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("padding", "composition"))

    def test_discovers_composition(self):
        train = (
            Example(
                Grid(((0, 0, 0), (0, 1, 2), (0, 0, 0))),
                Grid(((1, 1, 2, 2), (1, 1, 2, 2))),
            ),
        )
        test = (
            Example(
                Grid(((0, 0, 0), (0, 3, 4), (0, 0, 0))),
                Grid(((3, 3, 4, 4), (3, 3, 4, 4))),
            ),
        )
        disc = discover_task(Task(id="test_comp", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertEqual(disc.family, "composition")
        self.assertIn("crop", disc.families_used)
        self.assertIn("scale", disc.families_used)

    def test_identity_is_classified(self):
        train = (Example(Grid(((1, 2), (3, 4))), Grid(((1, 2), (3, 4)))),)
        test = (Example(Grid(((5, 6), (7, 8))), Grid(((5, 6), (7, 8)))),)
        disc = discover_task(Task(id="test_identity", train=train, test=test))
        self.assertTrue(disc.solved)
        self.assertEqual(disc.family, "identity")


@unittest.skipUnless(ARC_DATA.exists(), "ARC data not present")
class RealDataTests(unittest.TestCase):
    def _task(self, task_id: str) -> Task:
        from examples.arc.loader import load_task

        return load_task(ARC_DATA / f"{task_id}.json")

    def test_6150a2bd_rot180(self):
        disc = discover_task(self._task("6150a2bd"))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("rotation", "composition"))

    def test_74dd1130_transpose(self):
        disc = discover_task(self._task("74dd1130"))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("diagonal", "composition"))

    def test_1cf80156_crop(self):
        disc = discover_task(self._task("1cf80156"))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("crop", "composition"))

    def test_0d3d703e_recolor(self):
        disc = discover_task(self._task("0d3d703e"))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("recolor", "composition"))

    def test_67a3c6ac_flip(self):
        disc = discover_task(self._task("67a3c6ac"))
        self.assertTrue(disc.solved)
        self.assertIn(disc.family, ("flip", "composition"))


if __name__ == "__main__":
    unittest.main()
