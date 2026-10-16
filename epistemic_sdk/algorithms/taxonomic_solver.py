"""Training-only program selection and cross-task reuse of scoped definitions.

The solver has no test-output parameter. A family is a search hypothesis, and
each attempted task language is an explicit specialization of a shared node.
Only deterministic definitions are promoted. Evidence of fitting one task does
not make the corresponding rule true of every task in the family.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache, partial
from typing import Any

from epistemic_sdk import Application, Constant, Operator, Variable
from epistemic_sdk.m3.term import Term

from .arc_language import build_arc_taxonomy
from .fitted_families import FITTED_FAMILIES
from .fitting import GridFunction, Learner, Training
from .grid_objects import Grid
from .grid_transforms import recolor
from .language_discovery import LanguageDiscovery
from .language_taxonomy import LanguageRef, LanguageSnapshot, OperatorBinding
from .rewriting import substitute

UNDEFINED = object()


class GridEvaluator:
    """Per-search memoization, never shared across language/semantic versions."""

    def __init__(self, snapshot: LanguageSnapshot, max_cells: int = 2048) -> None:
        self._semantics = snapshot.semantics
        self._definitions = {item.operator.name: item for item in snapshot.learned}
        self._max_cells = max_cells
        self._evaluate = lru_cache(maxsize=20_000)(self._uncached)

    def _uncached(self, term: Term, grid: Grid) -> Any:
        if isinstance(term, Variable):
            return grid if term.name == "g" else UNDEFINED
        if isinstance(term, Constant):
            return term.value
        if term.operator in self._definitions:
            learned = self._definitions[term.operator]
            binding = dict(zip((v.name for v in learned.variables), term.arguments, strict=True))
            # Expand through the same evaluator so intermediate resource bounds
            # have identical semantics for primitive programs and learned macros.
            return self._evaluate(substitute(learned.definition, binding), grid)
        arguments = tuple(self._evaluate(arg, grid) for arg in term.arguments)
        if any(argument is UNDEFINED for argument in arguments):
            return UNDEFINED
        try:
            value = self._semantics[term.operator](*arguments)
        except ValueError:
            # Partial primitives document ValueError for inapplicable inputs.
            return UNDEFINED
        if isinstance(value, Grid) and value.height * value.width > self._max_cells:
            return UNDEFINED
        return value

    def __call__(self, term: Term, inputs: Mapping[str, Any]) -> Any:
        return self._evaluate(term, inputs["g"])


@dataclass(frozen=True)
class TaskProgram:
    program: Term | None
    snapshot: LanguageSnapshot | None
    scope: LanguageRef | None
    evaluated: int
    attempted_scopes: tuple[str, ...]
    reused: tuple[str, ...]

    def predict(self, grid: Grid) -> Grid | None:
        if self.program is None or self.snapshot is None:
            return None
        value = GridEvaluator(self.snapshot)(self.program, {"g": grid})
        return value if isinstance(value, Grid) else None


def operator_names(term: Term) -> tuple[str, ...]:
    if isinstance(term, Application):
        return (term.operator,) + tuple(
            name for argument in term.arguments for name in operator_names(argument)
        )
    return ()


def _mapping(training: Sequence[tuple[Grid, Grid]]) -> dict[int, int] | None:
    mapping: dict[int, int] = {}
    for source, target in training:
        if (source.height, source.width) != (target.height, target.width):
            return None
        for source_row, target_row in zip(source.cells, target.cells, strict=True):
            for before, after in zip(source_row, target_row, strict=True):
                if before in mapping and mapping[before] != after:
                    return None
                mapping[before] = after
    return mapping


def _fit_learners(learners: Mapping[str, Learner], training: Training) -> dict[str, GridFunction]:
    fitted = {}
    for name, learner in learners.items():
        function = learner(training)
        if function is not None:
            fitted[name] = function
    return fitted


def _task_bindings(training: Training, include_fitted: bool) -> tuple[OperatorBinding, ...]:
    """Operators estimated from this task's training pairs only."""
    bindings: list[OperatorBinding] = []
    mapping = _mapping(training)
    if mapping is not None:
        bindings.append(OperatorBinding(
            Operator("task_recolor", ("Grid",), "Grid"), partial(recolor, mapping=mapping),
        ))
    if include_fitted:
        for learners in FITTED_FAMILIES.values():
            bindings.extend(
                OperatorBinding(Operator(name, ("Grid",), "Grid"), function)
                for name, function in _fit_learners(learners, training).items())
    return tuple(bindings)


class TaxonomicSolver:
    """Deterministic family selection, bounded search, and optional memory.

    All selection features use training examples. The explicit initial policy
    searches global operations first, then relevant families. It is an engineering
    prior, not a learned or proven optimal language selector.
    """

    def __init__(self, *, max_candidates: int = 5000, max_nodes: int = 5,
                 flat: bool = False) -> None:
        self.taxonomy, self.scopes = build_arc_taxonomy()
        self.max_candidates = max_candidates
        self.max_nodes = max_nodes
        self.flat = flat
        self.promotions: list[dict[str, Any]] = []

    def solve(self, task_id: str, training: Sequence[tuple[Grid, Grid]]) -> TaskProgram:
        """Search enumerated families, then verify task-fitted families directly.

        Enumeration is charged to ``max_candidates``. Task-fitted learners are not:
        each is a bounded, deterministic fit whose output is checked on every
        training pair but never enumerated.
        """
        if not training:
            return TaskProgram(None, None, None, 0, (), ())
        cases = [({"g": source}, target) for source, target in training]
        attempted: list[str] = []
        total = 0
        for name, parent in self._enumerated_scopes(training):
            if total >= self.max_candidates:
                continue
            attempted.append(name)
            program, snapshot, evaluated = self._search_scope(
                task_id, name, parent, training, cases, self.max_candidates - total)
            total += evaluated
            if program is not None and snapshot is not None:
                return self._program(program, snapshot, parent, total, attempted)
        if self.flat:
            return TaskProgram(None, None, None, total, tuple(attempted), ())
        for family in FITTED_FAMILIES:
            attempted.append(family)
            found = self._verify_fitted(task_id, family, training, cases)
            if found is not None:
                program, snapshot = found
                return self._program(program, snapshot, self.scopes[family], total, attempted)
        return TaskProgram(None, None, None, total, tuple(attempted), ())

    def _enumerated_scopes(self, training: Sequence[tuple[Grid, Grid]],
                           ) -> list[tuple[str, LanguageRef]]:
        same_shape = all((a.height, a.width) == (b.height, b.width) for a, b in training)
        order = ["geometry"]
        order.extend(["symmetry", "topology", "dynamics", "object_selection"]
                     if same_shape else ["object_selection", "symmetry", "topology", "dynamics"])
        order.append("object_geometry")
        if self.flat:
            parent = self.taxonomy.define_node(
                "flat", parents=tuple(self.scopes[name] for name in order),
            )
            return [("flat", parent)]
        return [(name, self.scopes[name]) for name in order]

    def _specialize(self, task_id: str, name: str, parent: LanguageRef,
                    bindings: tuple[OperatorBinding, ...]) -> LanguageSnapshot:
        """Task-local node under a shared family; it is never reused across tasks."""
        ref = self.taxonomy.define_node(
            f"task:{task_id}:{name}", parents=(parent,), operators=bindings,
        )
        return self.taxonomy.resolve(ref)

    def _search_scope(
        self, task_id: str, name: str, parent: LanguageRef,
        training: Sequence[tuple[Grid, Grid]], cases: Sequence[tuple[dict[str, Grid], Grid]],
        budget: int,
    ) -> tuple[Term | None, LanguageSnapshot, int]:
        bindings = _task_bindings(training, include_fitted=name == "flat")
        snapshot = self._specialize(task_id, name, parent, bindings)
        # Learned abstractions are retrieval priors; all are still checked
        # against every training case before application to a new task.
        learned_names = {item.operator.name for item in snapshot.learned}
        language = replace(snapshot.language, operators=tuple(sorted(
            snapshot.language.operators,
            key=lambda op: (op.name not in learned_names, op.name == "task_recolor"),
        )))
        shallow = ("geometry", "symmetry", "topology", "dynamics")
        discovery = LanguageDiscovery(
            language, ("g",), GridEvaluator(snapshot), (),
            max_nodes=min(self.max_nodes, 3) if name in shallow else self.max_nodes,
            variable_sorts={"g": "Grid"}, result_sort="Grid",
        )
        result = discovery.fit(cases, max_candidates=budget)
        return result.program, snapshot, result.evaluated

    def _verify_fitted(
        self, task_id: str, family: str, training: Sequence[tuple[Grid, Grid]],
        cases: Sequence[tuple[dict[str, Grid], Grid]],
    ) -> tuple[Term, LanguageSnapshot] | None:
        fitted = _fit_learners(FITTED_FAMILIES[family], training)
        if not fitted:
            return None
        snapshot = self._specialize(task_id, family, self.scopes[family], tuple(
            OperatorBinding(Operator(name, ("Grid",), "Grid"), function)
            for name, function in fitted.items()
        ))
        evaluator = GridEvaluator(snapshot)
        for name in fitted:
            program = Application(name, (Variable("g", "Grid"),))
            if all(evaluator(program, inputs) == target for inputs, target in cases):
                return program, snapshot
        return None

    def _program(self, program: Term, snapshot: LanguageSnapshot, scope: LanguageRef,
                 evaluated: int, attempted: Sequence[str]) -> TaskProgram:
        learned = {item.operator.name for item in snapshot.learned}
        used = learned & set(operator_names(program))
        return TaskProgram(program, snapshot, scope, evaluated, tuple(attempted),
                           tuple(sorted(used)))

    def learn(self, task_id: str, training: Sequence[tuple[Grid, Grid]]) -> TaskProgram:
        """Fit and retain a reusable definition with training-only provenance.

        A two-example minimum is a conservative admission policy, not a proof.
        Empirical status stays candidate. Task-specific color maps are excluded.
        """
        result = self.solve(task_id, training)
        if (result.program is None or result.scope is None or len(training) < 2
                or self.flat):
            return result
        names = operator_names(result.program)
        if len(names) < 2 or any(name.startswith("task_") for name in names):
            return result
        name = "learned_" + hashlib.sha256(repr(result.program).encode()).hexdigest()[:12]
        snapshot = self.taxonomy.resolve(result.scope)
        if any(op.name == name for op in snapshot.language.operators):
            return result
        new_ref = self.taxonomy.promote(
            result.scope, name, result.program, (Variable("g", "Grid"),), "Grid", task_id,
            tuple(f"{task_id}:train:{index}" for index in range(len(training))),
        )
        self.scopes[result.scope.node_id] = new_ref
        if result.scope.node_id in ("geometry", "object_selection"):
            self.scopes["object_geometry"] = self.taxonomy.define_node(
                "object_geometry", parents=(self.scopes["geometry"],
                                            self.scopes["object_selection"]),
            )
        self.promotions.append({"task_id": task_id, "operator": name,
                                "scope": result.scope.node_id,
                                "definition": repr(result.program)})
        return result

    def export_memory(self) -> str:
        """Persist reusable families only, excluding task-local fitted callbacks."""
        records = json.loads(self.taxonomy.export_records())
        records["nodes"] = [record for record in records["nodes"]
                            if not record["ref"][0].startswith("task:")
                            and record["ref"][0] != "flat"]
        return json.dumps({
            "format": 1, "taxonomy": records,
            "scopes": {name: [ref.node_id, ref.version] for name, ref in self.scopes.items()},
            "promotions": self.promotions,
        }, sort_keys=True, indent=2)

    def import_memory(self, payload: str) -> None:
        """Restore the seed-compatible memory before solving any target task."""
        data = json.loads(payload)
        if data.get("format") != 1:
            raise ValueError("unsupported memory format")
        taxonomy, seed_scopes = build_arc_taxonomy()
        taxonomy.import_records(json.dumps(data["taxonomy"]))
        scopes = {name: LanguageRef(*ref) for name, ref in data["scopes"].items()}
        if set(scopes) != set(seed_scopes):
            raise ValueError("incompatible language families")
        for name, ref in scopes.items():
            if ref.node_id != name:
                raise ValueError("scope identity mismatch")
            taxonomy.resolve(ref)
        self.taxonomy, self.scopes = taxonomy, scopes
        self.promotions = list(data["promotions"])
