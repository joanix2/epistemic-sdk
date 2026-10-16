"""Typed inheritance and executable, provenance-preserving transfer."""
import json
import unittest

from epistemic_sdk.algorithms.language_taxonomy import (
    LanguageRef,
    LanguageTaxonomy,
    OperatorBinding,
)
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.operator import Operator
from epistemic_sdk.m3.sort import Sort
from epistemic_sdk.m3.variable import Variable


def increment(value: int) -> int:
    return value + 1


class LanguageTaxonomyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.taxonomy = LanguageTaxonomy()
        self.root = self.taxonomy.define_node(
            "numbers", sorts=(Sort("Int"), Sort("Bool")),
            operators=(OperatorBinding(Operator("succ", ("Int",), "Int"), increment),),
        )
        self.x = Variable("x", "Int")
        self.twice = Application("succ", (Application("succ", (self.x,)),))

    def promote(self, term=None, variables=None, result_sort="Int", name="plus_two"):
        return self.taxonomy.promote(
            self.root, name, self.twice if term is None else term,
            (self.x,) if variables is None else variables, result_sort,
            "source-task", ("training:source:1",),
        )

    def test_diamond_inherits_once_and_snapshots_are_immutable(self) -> None:
        left = self.taxonomy.define_node("left", parents=(self.root,))
        right = self.taxonomy.define_node("right", parents=(self.root,))
        combined = self.taxonomy.define_node("combined", parents=(left, right))
        snapshot = self.taxonomy.resolve(combined)
        self.assertEqual(snapshot.lineage, (self.root, left, right, combined))
        self.assertEqual(len(snapshot.language.operators), 1)
        self.assertEqual(snapshot.semantics["succ"](3), 4)
        with self.assertRaises(TypeError):
            snapshot.semantics["fake"] = increment  # type: ignore[index]

    def test_task_specializations_require_existing_parent(self) -> None:
        task = self.taxonomy.specialize("arc-1", self.root)
        self.assertEqual(self.taxonomy.nodes[task].parents, (self.root,))
        with self.assertRaises(ValueError):
            self.taxonomy.specialize("arc-2", LanguageRef("unknown", "1"))
        with self.assertRaises(ValueError):
            self.taxonomy.define_node("cycle", parents=(LanguageRef("cycle", "1"),))

    def test_transfer_executes_definition_preserving_provenance(self) -> None:
        old_task = self.taxonomy.specialize("before", self.root)
        improved = self.promote()
        new_task = self.taxonomy.specialize("after", improved)
        snapshot = self.taxonomy.resolve(new_task)
        self.assertEqual(snapshot.semantics["plus_two"](7), 9)
        record = snapshot.learned[0]
        self.assertEqual(record.scope, self.root)
        self.assertEqual(record.origin_task_ids, ("source-task",))
        self.assertEqual(record.evidence_ids, ("training:source:1",))
        self.assertEqual(record.status, "candidate")
        self.assertNotIn("plus_two", self.taxonomy.resolve(old_task).semantics)
        self.assertNotIn("plus_two", self.taxonomy.resolve(self.root).semantics)
        self.assertEqual(len(snapshot.language.axioms), 1)
        with self.assertRaises(TypeError):
            snapshot.semantics["plus_two"](1, 2)

    def test_nested_learned_definitions_execute(self) -> None:
        improved = self.promote()
        improved_again = self.taxonomy.promote(
            improved, "plus_four", Application("plus_two", (Application("plus_two", (self.x,)),)),
            (self.x,), "Int", "task-two", ("evidence:2",),
        )
        self.assertEqual(self.taxonomy.resolve(improved_again).semantics["plus_four"](4), 8)

    def test_task_discovery_does_not_propagate_to_parent(self) -> None:
        task = self.taxonomy.specialize("discoverer", self.root)
        improved = self.taxonomy.promote(
            task, "plus_two", self.twice, (self.x,), "Int", "discoverer", ("evidence",),
        )
        self.assertIn("plus_two", self.taxonomy.resolve(improved).semantics)
        sibling = self.taxonomy.specialize("sibling", self.root)
        self.assertNotIn("plus_two", self.taxonomy.resolve(sibling).semantics)

    def test_conflicting_parent_semantics_rejected_atomically(self) -> None:
        other = self.taxonomy.define_node(
            "other", sorts=(Sort("Int"),),
            operators=(OperatorBinding(Operator("succ", ("Int",), "Int"), lambda x: x + 2),),
        )
        before = len(self.taxonomy.nodes)
        with self.assertRaises(ValueError):
            self.taxonomy.define_node("ambiguous", parents=(self.root, other))
        self.assertEqual(len(self.taxonomy.nodes), before)

    def test_json_replay_preserves_definitions_topology_and_provenance(self) -> None:
        improved = self.promote()
        task = self.taxonomy.specialize("receiver", improved)
        payload = self.taxonomy.export_records()
        seed = LanguageTaxonomy()
        seed.define_node(
            "numbers", sorts=(Sort("Int"), Sort("Bool")),
            operators=(OperatorBinding(Operator("succ", ("Int",), "Int"), increment),),
        )
        seed.import_records(payload)
        self.assertEqual(seed.export_records(), payload)
        self.assertEqual(seed.resolve(task).learned, self.taxonomy.resolve(task).learned)
        self.assertEqual(seed.resolve(task).semantics["plus_two"](10), 12)
        seed.import_records(payload)
        self.assertEqual(seed.export_records(), payload)

    def test_import_is_atomic_and_requires_primitive_seed(self) -> None:
        self.promote()
        payload = self.taxonomy.export_records()
        empty = LanguageTaxonomy()
        with self.assertRaises(ValueError):
            empty.import_records(payload)
        self.assertEqual(len(empty.nodes), 0)
        data = json.loads(payload)
        data["nodes"][1]["learned"][0]["definition"]["operator"] = "missing"
        seed = LanguageTaxonomy()
        seed.define_node(
            "numbers", sorts=(Sort("Int"), Sort("Bool")),
            operators=(OperatorBinding(Operator("succ", ("Int",), "Int"), increment),),
        )
        before = seed.export_records()
        with self.assertRaises(ValueError):
            seed.import_records(json.dumps(data))
        self.assertEqual(seed.export_records(), before)

    def test_rejects_invalid_macro_types(self) -> None:
        invalid = (
            (Variable("free", "Int"), (self.x,), "Int"),
            (Variable("x", "Bool"), (self.x,), "Bool"),
            (Application("absent", (self.x,)), (self.x,), "Int"),
            (Application("succ", ()), (self.x,), "Int"),
            (Application("succ", (Constant(True, "Bool"),)), (self.x,), "Int"),
            (self.twice, (self.x,), "Bool"),
            (Constant(1, "Unknown"), (self.x,), "Int"),
            (self.twice, (self.x, self.x), "Int"),
            (self.twice, (self.x,), "Unknown"),
        )
        for term, variables, result in invalid:
            with self.subTest(term=term, result=result), self.assertRaises(ValueError):
                self.promote(term, variables, result)
        self.assertEqual(len(self.taxonomy.nodes), 1)

    def test_rejects_collisions_and_missing_provenance(self) -> None:
        with self.assertRaises(ValueError):
            self.promote(name="succ")
        with self.assertRaises(ValueError):
            self.taxonomy.promote(self.root, "new", self.twice, (self.x,), "Int", "task", ())
        with self.assertRaises(ValueError):
            self.taxonomy.define_node(
                "bad", operators=(OperatorBinding(Operator("succ", ("Int",), "Int"), increment),),
            )


if __name__ == "__main__":
    unittest.main()
