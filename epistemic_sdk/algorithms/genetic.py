"""Genetic synthesis: heuristic search over the program space.

A population of programs is evolved toward consistency with the training cases.
Fitness is the number of cases satisfied. Selection is by tournament, crossover
swaps random subterms, mutation replaces a random subterm with a fresh random
one. This is heuristic: unlike bounded enumeration it does NOT guarantee finding
a consistent program, and crossover/mutation may grow terms beyond ``max_nodes``
(only the initial population respects the bound).
"""

import random
from collections.abc import Sequence
from typing import Any

from epistemic_sdk.algorithms.synthesis import (
    SynthesisConfig,
    cases_from_graph,
    program_from_term,
)
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.knowledge.knowledge_base import KnowledgeBase
from epistemic_sdk.m1.hypothesis import Hypothesis
from epistemic_sdk.m1.inference_mode import InferenceMode
from epistemic_sdk.m1.program_m1 import ProgramM1
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable

_SORT = "S"


class GeneticSynthesisEngine:
    """Evolve programs toward consistency with the training cases."""

    def __init__(
        self,
        config: SynthesisConfig,
        *,
        population_size: int = 50,
        generations: int = 20,
        max_nodes: int = 7,
        mutation_rate: float = 0.2,
        crossover_rate: float = 0.7,
        seed: int | None = None,
    ) -> None:
        self.config = config
        self.population_size = population_size
        self.generations = generations
        self.max_nodes = max_nodes
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self._rng = random.Random(seed)

    def infer(
        self,
        graph: BeliefGraph[Any],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> Sequence[Hypothesis]:
        programs = self.evolve(graph, knowledge)
        supporting = tuple(belief.id for belief in graph.beliefs)
        return tuple(
            Hypothesis(
                id=f"H_gen_{i}",
                program=program,
                supporting_belief_ids=supporting,
                inference_mode=InferenceMode.ABDUCTION,
            )
            for i, program in enumerate(programs)
        )

    def evolve(
        self,
        graph: BeliefGraph[Any],
        knowledge: KnowledgeBase[ProgramM1],
        seeds: Sequence[ProgramM1] = (),
    ) -> tuple[ProgramM1, ...]:
        cases = cases_from_graph(graph, self.config.case_extractor)
        target = len(cases)

        def fitness(term: Term) -> int:
            return sum(
                1
                for inputs, expected in cases
                if self.config.evaluate(term, inputs) == expected
            )

        population: list[Term] = [seed.entrypoint for seed in seeds]
        while len(population) < self.population_size:
            population.append(self._random_term(self.max_nodes))
        population = population[: self.population_size]

        found: dict[tuple[Any, ...], Term] = {}

        for _ in range(self.generations):
            scored = sorted(((fitness(t), t) for t in population), key=lambda ft: -ft[0])
            for fit, term in scored:
                if fit == target:
                    signature = tuple(
                        self.config.evaluate(term, inputs) for inputs, _e in cases
                    )
                    found.setdefault(signature, term)

            elite_count = max(1, self.population_size // 10)
            next_population: list[Term] = [term for _f, term in scored[:elite_count]]
            while len(next_population) < self.population_size:
                parent1 = self._tournament(population, fitness)
                parent2 = self._tournament(population, fitness)
                if self._rng.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                next_population.append(self._mutate(child1))
                if len(next_population) < self.population_size:
                    next_population.append(self._mutate(child2))
            population = next_population

        for term in population:
            if fitness(term) == target:
                signature = tuple(self.config.evaluate(term, inputs) for inputs, _e in cases)
                found.setdefault(signature, term)

        return tuple(program_from_term(term, self.config) for term in found.values())

    # --- term generation and genetic operators ---

    def _leaves(self) -> list[Term]:
        leaves: list[Term] = [Variable(name, _SORT) for name in self.config.variables]
        leaves.extend(
            Application(name, ())
            for name, arity in self.config.grammar.items()
            if arity == 0
        )
        return leaves

    def _internal_operators(self) -> list[tuple[str, int]]:
        return [(name, arity) for name, arity in self.config.grammar.items() if arity > 0]

    def _random_term(self, budget: int) -> Term:
        leaves = self._leaves()
        internals = self._internal_operators()
        if not leaves:
            raise ValueError("grammar has no leaf (variable or nullary operator)")
        if not internals or budget <= 1 or self._rng.random() < 0.5:
            return self._rng.choice(leaves)
        name, arity = self._rng.choice(internals)
        if budget - 1 < arity:
            return self._rng.choice(leaves)
        sizes = self._random_composition(budget - 1, arity)
        return Application(name, tuple(self._random_term(size) for size in sizes))

    def _random_composition(self, total: int, parts: int) -> tuple[int, ...]:
        if parts == 1:
            return (total,)
        cuts = sorted(self._rng.sample(range(1, total), parts - 1))
        sizes: list[int] = []
        previous = 0
        for cut in [*cuts, total]:
            sizes.append(cut - previous)
            previous = cut
        return tuple(sizes)

    def _tournament(self, population: list[Term], fitness: Any, k: int = 3) -> Term:
        contestants = self._rng.sample(population, min(k, len(population)))
        return max(contestants, key=fitness)

    def _crossover(self, parent1: Term, parent2: Term) -> tuple[Term, Term]:
        path1 = self._rng.choice(self._subterm_paths(parent1))
        path2 = self._rng.choice(self._subterm_paths(parent2))
        sub1 = self._subterm_at(parent1, path1)
        sub2 = self._subterm_at(parent2, path2)
        return (
            self._replace_at_path(parent1, path1, sub2),
            self._replace_at_path(parent2, path2, sub1),
        )

    def _mutate(self, term: Term) -> Term:
        if self._rng.random() >= self.mutation_rate:
            return term
        path = self._rng.choice(self._subterm_paths(term))
        replacement = self._random_term(self._rng.randint(1, self.max_nodes))
        return self._replace_at_path(term, path, replacement)

    def _subterm_paths(self, term: Term) -> list[tuple[int, ...]]:
        paths: list[tuple[int, ...]] = [()]
        if isinstance(term, Application):
            for index, argument in enumerate(term.arguments):
                for sub_path in self._subterm_paths(argument):
                    paths.append((index, *sub_path))
        return paths

    def _subterm_at(self, term: Term, path: tuple[int, ...]) -> Term:
        current = term
        for index in path:
            assert isinstance(current, Application)
            current = current.arguments[index]
        return current

    def _replace_at_path(self, term: Term, path: tuple[int, ...], replacement: Term) -> Term:
        if not path:
            return replacement
        assert isinstance(term, Application)
        index = path[0]
        arguments = list(term.arguments)
        arguments[index] = self._replace_at_path(arguments[index], path[1:], replacement)
        return Application(term.operator, tuple(arguments))
