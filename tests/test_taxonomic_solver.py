"""Cross-task transfer, source/target separation and scoped executable memory."""
import unittest

from epistemic_sdk.algorithms.grid_objects import Grid
from epistemic_sdk.algorithms.taxonomic_solver import (
    UNDEFINED,
    GridEvaluator,
    TaxonomicSolver,
    operator_names,
)
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.variable import Variable
from tests.grid_helpers import grid


def source_examples():
    """Largest object to crop; neither its colors nor its bounding box are extremal."""
    return [
        (grid("203030 000003 011000 019020 300003 200000"), grid("11 19")),
        (grid("000006 060000 400000 000770 600780 040004"), grid("77 78")),
    ]


def target_examples():
    return [
        (grid("7000505 0000000 5088800 0088100 5000050 0500000 7000500"), grid("888 881")),
        (grid("0040009 0006660 9006690 0000009 9040900 0000009 4090000"), grid("666 669")),
    ]


class TaxonomicSolverTests(unittest.TestCase):
    def test_saved_definition_transfers_to_new_task_without_rediscovery(self):
        source = TaxonomicSolver()
        original = source.learn("source", source_examples())
        self.assertIsNotNone(original.program)
        self.assertEqual(len(source.promotions), 1)
        frozen = source.export_memory()
        target = TaxonomicSolver(max_nodes=2)
        target.import_memory(frozen)
        prediction = target.solve("target", target_examples())
        self.assertTrue(prediction.reused)
        self.assertIsNone(TaxonomicSolver(max_nodes=2).solve("target", target_examples()).program)
        self.assertEqual(prediction.predict(target_examples()[0][0]), target_examples()[0][1])
        self.assertEqual(target.export_memory(), frozen)
        assert prediction.snapshot is not None
        learned = prediction.snapshot.learned[0]
        self.assertEqual(learned.origin_task_ids, ("source",))
        self.assertEqual(learned.evidence_ids, ("source:train:0", "source:train:1"))
        self.assertEqual(learned.status, "candidate")
        self.assertTrue(prediction.snapshot.language.id.startswith("task:target:"))

    def test_child_language_inherits_promoted_parent_definition(self):
        solver = TaxonomicSolver()
        old_ref = solver.scopes["object_geometry"]
        old = solver.taxonomy.resolve(old_ref)
        solver.learn("source", source_examples())
        new = solver.taxonomy.resolve(solver.scopes["object_geometry"])
        self.assertFalse(old.learned)
        self.assertEqual(len(new.learned), 1)
        name = new.learned[0].operator.name
        value = new.semantics[name](target_examples()[0][0])
        self.assertEqual(value, target_examples()[0][1])
        self.assertEqual(solver.taxonomy.resolve(old_ref), old)

    def test_single_example_or_task_fitted_map_is_not_promoted(self):
        solver = TaxonomicSolver()
        solver.learn("one", source_examples()[:1])
        solver.learn("colors", [(Grid(((1, 0),)), Grid(((3, 0),))),
                                (Grid(((0, 1),)), Grid(((0, 3),)))])
        self.assertFalse(solver.promotions)

    def test_memory_is_checked_against_target_training(self):
        solver = TaxonomicSolver()
        solver.learn("source", source_examples())
        solver.max_nodes = 2
        wrong = [(grid, Grid(((9,),))) for grid, _ in target_examples()]
        result = solver.solve("different_rule", wrong)
        self.assertIsNone(result.program)

    def test_object_sort_is_preserved_in_discovered_program(self):
        solver = TaxonomicSolver()
        result = solver.solve("objects", source_examples())
        self.assertIsInstance(result.program, Application)
        assert result.snapshot is not None
        self.assertIn("Object", [sort.name for sort in result.snapshot.language.sorts])
        self.assertIn("Objects", [sort.name for sort in result.snapshot.language.sorts])
        self.assertIn(Variable("g", "Grid").sort,
                      [sort.name for sort in result.snapshot.language.sorts])

    def test_candidate_budget_and_empty_training(self):
        solver = TaxonomicSolver(max_candidates=10)
        result = solver.solve("budget", source_examples())
        self.assertLessEqual(result.evaluated, 10)
        self.assertIsNone(result.program)
        self.assertEqual(solver.solve("empty", []).evaluated, 0)

    def test_separation_intersection_and_recoloring_are_readable_steps(self):
        training = [
            (grid("1105011 0115100 1015101"), grid("020 000 202")),
            (grid("1115110 0005001 1005111"), grid("220 000 200")),
        ]
        result = TaxonomicSolver(max_nodes=6).solve("intersect", training)
        assert result.program is not None
        names = operator_names(result.program)
        self.assertIn("and", names)
        self.assertTrue({"keep_left", "keep_right"} <= set(names))
        self.assertEqual(result.scope.node_id if result.scope else None, "logic")
        self.assertEqual(result.predict(grid("1015111")), grid("202"))
        self.assertLessEqual({n for n in names if n.startswith("task_")}, {"task_recolor"})

    def test_macros_preserve_intermediate_execution_bounds(self):
        solver = TaxonomicSolver()
        g = Variable("g", "Grid")
        term = Application("crop", (Application("upscale_3", (g,)),))
        ref = solver.taxonomy.promote(solver.scopes["geometry"], "macro", term,
                                     (g,), "Grid", "source", ("source:train:0",))
        evaluate = GridEvaluator(solver.taxonomy.resolve(ref))
        grid = Grid(tuple(tuple(int(r == c == 0) for c in range(20)) for r in range(20)))
        self.assertIs(evaluate(term, {"g": grid}), UNDEFINED)
        self.assertIs(evaluate(Application("macro", (g,)), {"g": grid}), UNDEFINED)

    def test_target_labels_only_change_validation(self):
        from examples.arc.loader import Example, Task
        from examples.arc.transfer_measure import evaluate_task

        examples = tuple(Example(a, b) for a, b in source_examples())
        source, expected = target_examples()[0]
        good = Task("target", examples, (Example(source, expected),))
        bad = Task("target", examples, (Example(source, Grid(((9,),))),))
        first = evaluate_task(TaxonomicSolver(), good)
        second = evaluate_task(TaxonomicSolver(), bad)
        self.assertEqual(first["program"], second["program"])
        self.assertEqual(first["predictions"], second["predictions"])
        self.assertTrue(first["solved"])
        self.assertFalse(second["solved"])
        self.assertEqual(second["validations"][0]["counterexample_ids"], ["target:test:0"])
