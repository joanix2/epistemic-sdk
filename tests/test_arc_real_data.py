"""Recolor discovery on a real ARC task (skipped when the data is absent)."""
import os
import unittest
from pathlib import Path

from examples.arc.loader import load_task
from examples.arc.transformations import discover_recolor, recolor

ARC_DATA = Path(
    os.environ.get("ARC_DATA_DIR", "/home/joan/Documents/Programation/ARC-AGI/data/training")
)


@unittest.skipUnless(ARC_DATA.exists(), "ARC data not present")
class Tests(unittest.TestCase):
    def test_recolor_solves_a_real_task(self):
        task = load_task(ARC_DATA / "0d3d703e.json")
        mapping = discover_recolor(task.train)
        self.assertTrue(mapping)
        self.assertTrue(
            all(recolor(example.input, mapping) == example.output for example in task.test)
        )


if __name__ == "__main__":
    unittest.main()
