"""Tests for the ARC measurement harness (``examples.arc.measure``)."""
import os
import unittest
from pathlib import Path

from examples.arc.loader import Example, Grid, Task, load_training_tasks
from examples.arc.measure import MeasurementReport, format_report, measure

ARC_DATA = Path(
    os.environ.get("ARC_DATA_DIR", "/home/joan/Documents/Programation/ARC-AGI/data/training")
)


def _rotate_180_task() -> Task:
    return Task(
        id="measure_rot180",
        train=(
            Example(
                Grid(((0, 0, 1), (0, 0, 2), (0, 0, 0))),
                Grid(((0, 0, 0), (2, 0, 0), (1, 0, 0))),
            ),
            Example(Grid(((1, 2), (3, 4))), Grid(((4, 3), (2, 1)))),
        ),
        test=(Example(Grid(((5, 6), (7, 8))), Grid(((8, 7), (6, 5)))),),
    )


def _crop_task() -> Task:
    return Task(
        id="measure_crop",
        train=(Example(Grid(((0, 0, 0), (0, 1, 2), (0, 0, 0))), Grid(((1, 2),))),),
        test=(Example(Grid(((0, 0, 0), (0, 3, 4), (0, 0, 0))), Grid(((3, 4),))),),
    )


def _recolor_task() -> Task:
    return Task(
        id="measure_recolor",
        train=(
            Example(Grid(((0, 4), (4, 0))), Grid(((0, 1), (1, 0)))),
            Example(Grid(((4, 4), (0, 4))), Grid(((1, 1), (0, 1)))),
        ),
        test=(Example(Grid(((0, 4), (4, 4))), Grid(((0, 1), (1, 1)))),),
    )


class MeasureTests(unittest.TestCase):
    def test_measures_synthetic_tasks(self):
        tasks = (_rotate_180_task(), _crop_task(), _recolor_task())
        report = measure(tasks)
        self.assertEqual(report.total, 3)
        self.assertEqual(report.solved, 3)
        self.assertEqual(
            dict(report.by_family), {"crop": 1, "recolor": 1, "rotation": 1}
        )

    def test_format_report_contains_totals(self):
        tasks = (_rotate_180_task(), _crop_task(), _recolor_task())
        text = format_report(measure(tasks))
        self.assertIn("3/3", text)
        self.assertIn("100.0", text)

    def test_measure_empty_is_zeroed(self):
        report = measure(())
        self.assertEqual(report.total, 0)
        self.assertEqual(report.solved, 0)
        self.assertEqual(report.by_family, ())

    def test_report_is_frozen_value_type(self):
        self.assertEqual(
            MeasurementReport(0, 0, (), ()), MeasurementReport(0, 0, (), ())
        )


@unittest.skipUnless(ARC_DATA.exists(), "ARC data not present")
class RealDataMeasureTests(unittest.TestCase):
    def test_first_sixty_aggregate(self):
        tasks = load_training_tasks(ARC_DATA)[:60]
        report = measure(tasks, max_nodes=3)
        self.assertEqual(report.total, 60)
        self.assertGreaterEqual(report.solved, 1)
        self.assertTrue(dict(report.by_family))


if __name__ == "__main__":
    unittest.main()
