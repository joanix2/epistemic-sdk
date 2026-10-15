"""Equality graph (e-graph): semantic equivalence, saturation, and extraction.

The core data structure of M3 equational reasoning. Terms are added as e-nodes,
semantically equal terms are merged into e-classes (with congruence closure),
rewrite rules saturate the graph, and extraction returns the cheapest
representative of a class. This is the principled foundation for both the
rewriting engine and semantic abstraction discovery — no LLM, no gradient.
"""
from dataclasses import dataclass
from typing import Any

from epistemic_sdk.m3.application import Application
from epistemic_sdk.m3.constant import Constant
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.variable import Variable


@dataclass(frozen=True)
class ENode:
    key: Any
    children: tuple[int, ...] = ()


def _key(term: Term) -> Any:
    if isinstance(term, Variable):
        return ("var", term.name, term.sort)
    if isinstance(term, Constant):
        return ("const", term.value, term.sort)
    if isinstance(term, Application):
        return ("app", term.operator)
    raise TypeError(f"unexpected term {term!r}")


class EGraph:
    def __init__(self) -> None:
        self._classes: dict[int, set[ENode]] = {}
        self._parent: dict[int, int] = {}
        self._hashcons: dict[ENode, int] = {}

    def add(self, term: Term) -> int:
        if isinstance(term, (Variable, Constant)):
            return self._node(ENode(_key(term)))
        children = tuple(self.add(argument) for argument in term.arguments)
        return self._node(ENode(_key(term), children))

    def find(self, class_id: int) -> int:
        root = class_id
        while self._parent[root] != root:
            root = self._parent[root]
        current = class_id
        while self._parent[current] != current:
            nxt = self._parent[current]
            self._parent[current] = root
            current = nxt
        return root

    def merge(self, a: int, b: int) -> int:
        result = self._union(a, b)
        self._rebuild()
        return result

    def extract(self, class_id: int) -> Term:
        cost = self._cost_table()
        return self._extract(self.find(class_id), cost)

    def _cost_table(self) -> dict[int, float]:
        cost: dict[int, float] = {class_id: float("inf") for class_id in self._classes}
        changed = True
        while changed:
            changed = False
            for class_id, nodes in self._classes.items():
                canonical = self.find(class_id)
                for node in nodes:
                    if node.key[0] in ("var", "const"):
                        node_cost = 1.0
                    else:
                        node_cost = 1.0 + sum(
                            cost.get(self.find(child), float("inf"))
                            for child in node.children
                        )
                    if node_cost < cost[canonical]:
                        cost[canonical] = node_cost
                        changed = True
        return cost

    def _extract(self, class_id: int, cost: dict[int, float]) -> Term:
        class_id = self.find(class_id)
        best_node: ENode | None = None
        best_cost = float("inf")
        for node in self._classes[class_id]:
            if node.key[0] in ("var", "const"):
                node_cost = 1.0
            else:
                node_cost = 1.0 + sum(
                    cost[self.find(child)] for child in node.children
                )
            if node_cost < best_cost:
                best_cost = node_cost
                best_node = node
        assert best_node is not None
        if best_node.key[0] == "var":
            return Variable(best_node.key[1], best_node.key[2])
        if best_node.key[0] == "const":
            return Constant(best_node.key[1], best_node.key[2])
        arguments = tuple(self._extract(child, cost) for child in best_node.children)
        return Application(best_node.key[1], arguments)

    def saturate(self, rules: list[tuple[Term, Term]], limit: int = 100) -> int:
        merges = 0
        for _ in range(limit):
            progress = False
            for lhs, rhs in rules:
                for class_id, substitution in self._ematch(lhs):
                    rhs_class = self._add_substituted(rhs, substitution)
                    if self.find(rhs_class) != self.find(class_id):
                        self.merge(class_id, rhs_class)
                        merges += 1
                        progress = True
            if not progress:
                break
        return merges

    # ---- internals ----

    def _node(self, node: ENode) -> int:
        canonical = ENode(node.key, tuple(self.find(c) for c in node.children))
        if canonical in self._hashcons:
            return self._hashcons[canonical]
        new_id = len(self._classes)
        self._classes[new_id] = {canonical}
        self._parent[new_id] = new_id
        self._hashcons[canonical] = new_id
        return new_id

    def _union(self, a: int, b: int) -> int:
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return a
        if len(self._classes[a]) < len(self._classes[b]):
            a, b = b, a
        self._classes[a] |= self._classes[b]
        del self._classes[b]
        self._parent[b] = a
        return a

    def _rebuild(self) -> None:
        while True:
            canonical_map: dict[ENode, list[int]] = {}
            for class_id, nodes in self._classes.items():
                for node in nodes:
                    canonical = ENode(node.key, tuple(self.find(c) for c in node.children))
                    canonical_map.setdefault(canonical, []).append(class_id)
            merged = False
            for _canonical, class_ids in canonical_map.items():
                if len(class_ids) > 1:
                    target = class_ids[0]
                    for other in class_ids[1:]:
                        if self.find(other) != self.find(target):
                            self._union(target, other)
                            merged = True
            self._hashcons = {node: self.find(c) for node, c in self._hashcons.items()}
            if not merged:
                break

    def _ematch(self, pattern: Term) -> list[tuple[int, dict[str, int]]]:
        results: list[tuple[int, dict[str, int]]] = []
        for class_id in list(self._classes):
            for substitution in self._match(pattern, class_id, {}):
                results.append((class_id, substitution))
        return results

    def _match(
        self, pattern: Term, class_id: int, substitution: dict[str, int]
    ) -> list[dict[str, int]]:
        class_id = self.find(class_id)
        if isinstance(pattern, Variable):
            if pattern.name in substitution:
                return [substitution] if substitution[pattern.name] == class_id else []
            return [{**substitution, pattern.name: class_id}]
        if isinstance(pattern, Constant):
            leaf = self._hashcons.get(ENode(_key(pattern)))
            return [substitution] if leaf is not None and self.find(leaf) == class_id else []
        results: list[dict[str, int]] = []
        for node in self._classes.get(class_id, ()):
            if node.key == ("app", pattern.operator) and len(node.children) == len(
                pattern.arguments
            ):
                current = [substitution]
                for argument_pattern, child in zip(pattern.arguments, node.children, strict=True):
                    current = [
                        next_subst
                        for subst in current
                        for next_subst in self._match(argument_pattern, child, subst)
                    ]
                results.extend(current)
        return results

    def _add_substituted(self, term: Term, substitution: dict[str, int]) -> int:
        if isinstance(term, Variable):
            return substitution[term.name]
        if isinstance(term, Constant):
            return self._node(ENode(_key(term)))
        children = tuple(
            self._add_substituted(argument, substitution) for argument in term.arguments
        )
        return self._node(ENode(_key(term), children))
