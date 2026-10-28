"""Versioned, internal M2 taxonomy and reusable definitional operators.

Nodes inherit exact parent versions. Definitions are type checked syntactically;
primitive Python callables remain trusted for purity and runtime sort membership.
Evidence records describe a discovery's scope, never a proof of generality.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal

from epistemic_sdk.m2.language_m2 import LanguageM2
from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.axiom import Axiom
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.equation import Equation
from epistemic_sdk.m3.operator import Operator
from epistemic_sdk.m3.sort import Sort
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


@dataclass(frozen=True)
class LanguageRef:
    node_id: str
    version: str


@dataclass(frozen=True)
class OperatorBinding:
    operator: Operator
    semantics: Callable[..., Any]


@dataclass(frozen=True)
class LearnedOperator:
    operator: Operator
    definition: Term
    variables: tuple[Variable, ...]
    scope: LanguageRef
    origin_task_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    status: Literal["candidate", "corroborated"] = "candidate"


@dataclass(frozen=True)
class LanguageNode:
    ref: LanguageRef
    parents: tuple[LanguageRef, ...]
    sorts: tuple[Sort, ...]
    operators: tuple[OperatorBinding, ...]
    learned: tuple[LearnedOperator, ...] = ()


@dataclass(frozen=True)
class LanguageSnapshot:
    language: LanguageM2
    semantics: Mapping[str, Callable[..., Any]]
    lineage: tuple[LanguageRef, ...]
    learned: tuple[LearnedOperator, ...]


class LanguageTaxonomy:
    """Append-only DAG of immutable language versions.

    Registration accepts only already existing parents, preventing cycles.
    Updating a family does not silently update its children. A task must explicitly
    specialize the newer version to receive it. Callable state is not frozen.
    """

    def __init__(self) -> None:
        self._nodes: dict[LanguageRef, LanguageNode] = {}
        self._snapshots: dict[LanguageRef, LanguageSnapshot] = {}

    @property
    def nodes(self) -> Mapping[LanguageRef, LanguageNode]:
        return MappingProxyType(self._nodes)

    def define_node(
        self,
        node_id: str,
        *,
        parents: tuple[LanguageRef, ...] = (),
        sorts: tuple[Sort, ...] = (),
        operators: tuple[OperatorBinding, ...] = (),
    ) -> LanguageRef:
        return self._insert(node_id, parents, sorts, operators, ())

    def specialize(self, task_id: str, parent_ref: LanguageRef) -> LanguageRef:
        if not task_id:
            raise ValueError("task_id must be nonempty")
        return self.define_node(f"task:{task_id}", parents=(parent_ref,))

    def resolve(self, ref: LanguageRef) -> LanguageSnapshot:
        return self._snapshots[ref]

    def promote(
        self,
        scope_ref: LanguageRef,
        name: str,
        term: Term,
        variables: tuple[Variable, ...],
        result_sort: str,
        origin_task_id: str,
        evidence_ids: tuple[str, ...],
        *,
        status: Literal["candidate", "corroborated"] = "candidate",
    ) -> LanguageRef:
        """Register a reusable definition at an explicitly chosen scope.

        This operation does not infer that an empirical principle generalizes.
        The caller chooses the scope and supplies evidence; candidate is the
        default status. Nothing is added to ancestors or existing snapshots.
        """
        if not name or not origin_task_id or not evidence_ids or not all(evidence_ids):
            raise ValueError("name, origin task and nonempty evidence IDs are required")
        if status not in ("candidate", "corroborated"):
            raise ValueError("unsupported discovery status")
        snapshot = self.resolve(scope_ref)
        operators = {operator.name: operator for operator in snapshot.language.operators}
        if name in operators:
            raise ValueError(f"operator already exists: {name}")
        sorts = {sort.name for sort in snapshot.language.sorts}
        variable_sorts = {variable.name: variable.sort for variable in variables}
        if len(variable_sorts) != len(variables):
            raise ValueError("duplicate argument names")
        if any(sort not in sorts for sort in (*variable_sorts.values(), result_sort)):
            raise ValueError("undeclared sort")
        actual_sort = self._term_sort(term, variable_sorts, operators, sorts)
        if actual_sort != result_sort:
            raise ValueError(f"result sort mismatch: {actual_sort} != {result_sort}")
        learned = LearnedOperator(
            Operator(name, tuple(variable.sort for variable in variables), result_sort),
            term, variables, scope_ref, (origin_task_id,), evidence_ids, status,
        )
        return self._insert(scope_ref.node_id, (scope_ref,), (), (), (learned,))

    def export_records(self) -> str:
        """Serialize topology and discoveries, excluding primitive callables.

        Replay requires the same named primitive seed nodes to be registered.
        A primitive's source code or behavior cannot be certified by this format.
        """
        def ref_data(ref: LanguageRef) -> list[str]:
            return [ref.node_id, ref.version]

        records = []
        for node in self._nodes.values():
            records.append({
                "ref": ref_data(node.ref),
                "parents": [ref_data(parent) for parent in node.parents],
                "sorts": [sort.name for sort in node.sorts],
                "primitives": [
                    [
                        binding.operator.name, list(binding.operator.arguments),
                        binding.operator.result,
                    ]
                    for binding in node.operators
                ],
                "learned": [{
                    "name": learned.operator.name,
                    "definition": self._encode_term(learned.definition),
                    "variables": [[var.name, var.sort] for var in learned.variables],
                    "result_sort": learned.operator.result,
                    "scope": ref_data(learned.scope),
                    "origin_task_ids": list(learned.origin_task_ids),
                    "evidence_ids": list(learned.evidence_ids),
                    "status": learned.status,
                } for learned in node.learned],
            })
        return json.dumps({"format": 1, "nodes": records}, sort_keys=True)

    def import_records(self, payload: str) -> None:
        """Atomically replay records against an explicitly registered seed.

        Definitions are rechecked. Stored provenance is retained as a claim,
        not authenticated as evidence by loading it.
        """
        data = json.loads(payload)
        if data.get("format") != 1:
            raise ValueError("unsupported taxonomy format")
        staging = LanguageTaxonomy()
        staging._nodes = dict(self._nodes)
        staging._snapshots = dict(self._snapshots)
        existing = {
            tuple(record["ref"]): record
            for record in json.loads(self.export_records())["nodes"]
        }
        for record in data["nodes"]:
            key = tuple(record["ref"])
            if key in existing:
                if existing[key] != record:
                    raise ValueError(f"incompatible existing node: {key}")
                continue
            ref = LanguageRef(*record["ref"])
            version = str(1 + sum(r.node_id == ref.node_id for r in staging._nodes))
            if ref.version != version:
                raise ValueError("nonsequential node version")
            if record["primitives"]:
                raise ValueError("register primitive seed before importing")
            parents = tuple(LanguageRef(*parent) for parent in record["parents"])
            if record["learned"]:
                if len(record["learned"]) != 1 or record["sorts"]:
                    raise ValueError("invalid promotion record")
                learned = record["learned"][0]
                scope = LanguageRef(*learned["scope"])
                if parents != (scope,) or ref.node_id != scope.node_id:
                    raise ValueError("promotion scope differs from parent")
                if len(learned["origin_task_ids"]) != 1:
                    raise ValueError("promotion requires one origin task")
                staging.promote(
                    scope, learned["name"], self._decode_term(learned["definition"]),
                    tuple(Variable(*var) for var in learned["variables"]),
                    learned["result_sort"], learned["origin_task_ids"][0],
                    tuple(learned["evidence_ids"]), status=learned["status"],
                )
            else:
                staging.define_node(
                    ref.node_id, parents=parents,
                    sorts=tuple(Sort(name) for name in record["sorts"]),
                )
        self._nodes.update(staging._nodes)
        self._snapshots.update(staging._snapshots)

    @staticmethod
    def _encode_term(term: Term) -> dict[str, Any]:
        if isinstance(term, Variable):
            return {"kind": "variable", "name": term.name, "sort": term.sort}
        if isinstance(term, Constant):
            return {"kind": "constant", "value": term.value, "sort": term.sort}
        return {
            "kind": "application", "operator": term.operator,
            "arguments": [LanguageTaxonomy._encode_term(arg) for arg in term.arguments],
        }

    @staticmethod
    def _decode_term(data: Mapping[str, Any]) -> Term:
        if data["kind"] == "variable":
            return Variable(data["name"], data["sort"])
        if data["kind"] == "constant":
            if not isinstance(data["value"], (str, int, float, bool)):
                raise ValueError("invalid constant value")
            return Constant(data["value"], data["sort"])
        if data["kind"] == "application":
            return Application(
                data["operator"],
                tuple(LanguageTaxonomy._decode_term(arg) for arg in data["arguments"]),
            )
        raise ValueError("unknown term kind")

    def _insert(
        self,
        node_id: str,
        parents: tuple[LanguageRef, ...],
        sorts: tuple[Sort, ...],
        operators: tuple[OperatorBinding, ...],
        learned: tuple[LearnedOperator, ...],
    ) -> LanguageRef:
        if not node_id:
            raise ValueError("node_id must be nonempty")
        if len(set(parents)) != len(parents):
            raise ValueError("duplicate parents")
        for parent in parents:
            if parent not in self._nodes:
                raise ValueError(f"unknown parent: {parent}")
        version = str(1 + sum(ref.node_id == node_id for ref in self._nodes))
        ref = LanguageRef(node_id, version)
        node = LanguageNode(ref, parents, sorts, operators, learned)
        snapshot = self._materialize(node)
        self._nodes[ref] = node
        self._snapshots[ref] = snapshot
        return ref

    def _materialize(self, node: LanguageNode) -> LanguageSnapshot:
        sort_map: dict[str, Sort] = {}
        bindings: dict[str, OperatorBinding | LearnedOperator] = {}
        semantics: dict[str, Callable[..., Any]] = {}
        lineage: list[LanguageRef] = []

        def visit(ref: LanguageRef) -> None:
            if ref in lineage:
                return
            ancestor = self._nodes[ref]
            for parent in ancestor.parents:
                visit(parent)
            lineage.append(ref)

        for parent in node.parents:
            visit(parent)
        ancestors = [self._nodes[ref] for ref in lineage] + [node]
        for ancestor in ancestors:
            for sort in ancestor.sorts:
                if not sort.name:
                    raise ValueError("sort name must be nonempty")
                sort_map[sort.name] = sort
            local_bindings: tuple[OperatorBinding | LearnedOperator, ...] = (
                *ancestor.operators, *ancestor.learned,
            )
            for binding in local_bindings:
                name = binding.operator.name
                if not name:
                    raise ValueError("operator name must be nonempty")
                if name in bindings:
                    if bindings[name] != binding:
                        raise ValueError(f"conflicting operator: {name}")
                    continue
                bindings[name] = binding
                if isinstance(binding, OperatorBinding):
                    if not callable(binding.semantics):
                        raise ValueError(f"missing semantics: {name}")
                    semantics[name] = binding.semantics
                else:
                    semantics[name] = self._compile(binding, dict(semantics))
        for binding in bindings.values():
            operator = binding.operator
            if any(sort not in sort_map for sort in (*operator.arguments, operator.result)):
                raise ValueError(f"undeclared sort in operator: {operator.name}")
        learned = tuple(item for item in bindings.values() if isinstance(item, LearnedOperator))
        axioms = tuple(
            Axiom(
                id=f"{item.operator.name}_def",
                statement=Equation(
                    Application(item.operator.name, item.variables), item.definition,
                ),
                origin="definition",
            )
            for item in learned
        )
        language = LanguageM2(
            node.ref.node_id, node.ref.version, tuple(sort_map.values()),
            tuple(binding.operator for binding in bindings.values()), axioms,
        )
        return LanguageSnapshot(
            language, MappingProxyType(semantics), (*lineage, node.ref), learned,
        )

    @staticmethod
    def _compile(
        learned: LearnedOperator, semantics: Mapping[str, Callable[..., Any]],
    ) -> Callable[..., Any]:
        def operation(*values: Any) -> Any:
            if len(values) != len(learned.variables):
                raise TypeError(f"wrong arity for {learned.operator.name}")
            environment = dict(zip((var.name for var in learned.variables), values, strict=True))

            def evaluate(term: Term) -> Any:
                if isinstance(term, Variable):
                    return environment[term.name]
                if isinstance(term, Constant):
                    return term.value
                return semantics[term.operator](*(evaluate(arg) for arg in term.arguments))

            return evaluate(learned.definition)

        return operation

    @staticmethod
    def _term_sort(
        term: Term,
        variables: Mapping[str, str],
        operators: Mapping[str, Operator],
        sorts: set[str],
    ) -> str:
        if isinstance(term, Variable):
            if variables.get(term.name) != term.sort:
                raise ValueError(f"unbound or incorrectly typed variable: {term.name}")
            return term.sort
        if isinstance(term, Constant):
            if term.sort not in sorts:
                raise ValueError(f"undeclared constant sort: {term.sort}")
            return term.sort
        if term.operator not in operators:
            raise ValueError(f"undefined operator: {term.operator}")
        operator = operators[term.operator]
        actual = tuple(
            LanguageTaxonomy._term_sort(argument, variables, operators, sorts)
            for argument in term.arguments
        )
        if actual != operator.arguments:
            raise ValueError(f"argument sorts or arity mismatch: {term.operator}")
        return operator.result
