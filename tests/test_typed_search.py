"""Typed synthesis and honest selection, independent of held-out answers."""
import unittest

from epistemic_sdk import Application, LanguageM2, Operator, Sort, Variable
from epistemic_sdk.algorithms.language_discovery import LanguageDiscovery
from epistemic_sdk.algorithms.typed_search import enumerate_typed_terms


class TypedSearchTests(unittest.TestCase):
    def test_cross_sort_composition_and_actual_variable_sort(self):
        language = LanguageM2("typed", "1", (Sort("Number"), Sort("Bool")), (
            Operator("positive", ("Number",), "Bool"),
            Operator("negate", ("Bool",), "Bool"),
        ))
        x = Variable("x", "Number")
        self.assertEqual(list(enumerate_typed_terms(language, (x,), "Bool", 3)), [
            Application("positive", (x,)),
            Application("negate", (Application("positive", (x,)),)),
        ])

    def test_distinct_training_consistent_hypotheses_survive(self):
        language = LanguageM2("numbers", "1", (Sort("Number"),), (
            Operator("square", ("Number",), "Number"),
        ))

        def evaluate(term, inputs):
            if isinstance(term, Variable):
                return inputs[term.name]
            return evaluate(term.arguments[0], inputs) ** 2

        discovery = LanguageDiscovery(language, ("x",), evaluate, (), max_nodes=2)
        result = discovery.fit([({"x": 0}, 0), ({"x": 1}, 1)], max_results=5)
        self.assertEqual(len(result.candidates), 2)
        self.assertEqual([evaluate(t, {"x": 2}) for t in result.candidates], [2, 4])
        self.assertEqual(result.program, Variable("x", "Number"))
        self.assertTrue(result.exhausted)

    def test_budget_does_not_claim_exhaustion(self):
        language = LanguageM2("numbers", "1", (Sort("N"),), (
            Operator("succ", ("N",), "N"),
        ))
        discovery = LanguageDiscovery(language, ("x",), lambda t, i: 0, (), max_nodes=3)
        result = discovery.fit([({"x": 0}, 9)], max_candidates=1)
        self.assertIsNone(result.program)
        self.assertFalse(result.exhausted)
        self.assertEqual(result.evaluated, 1)

    def test_arc_program_is_independent_of_test_output(self):
        from examples.arc.discovery import discover_task
        from examples.arc.loader import Example, Grid, Task

        symmetric = Grid(((1, 1), (1, 1)))
        asymmetric = Grid(((1, 2), (3, 4)))
        train = (Example(symmetric, symmetric),)
        first = discover_task(Task("same", train, (Example(asymmetric, asymmetric),)),
                              max_nodes=2)
        second = discover_task(Task("same", train, (Example(asymmetric, symmetric),)),
                               max_nodes=2)
        self.assertEqual(first.program, second.program)
        self.assertTrue(first.solved)
        self.assertFalse(second.solved)

    def test_intermediate_generation_is_bounded(self):
        language = LanguageM2("intermediate", "1", (Sort("Grid"), Sort("A")), (
            Operator("seed", (), "A"), Operator("next", ("A",), "A"),
            Operator("render", ("A",), "Grid"),
        ))
        discovery = LanguageDiscovery(language, ("g",), lambda t, i: None, (),
                                      max_nodes=20, variable_sorts={"g": "Grid"},
                                      result_sort="Grid")
        result = discovery.fit([({"g": 0}, 1)], max_generated=4)
        self.assertEqual(result.generated, 4)
        self.assertFalse(result.exhausted)
