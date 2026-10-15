from collections.abc import Sequence
from typing import Protocol, TypeVar

from epistemic_sdk.m1.hypothesis import Hypothesis
from epistemic_sdk.validation.validation_report import ValidationReport

from .knowledge_base import KnowledgeBase

P = TypeVar("P")

class KnowledgeReviser(Protocol[P]):
    """Update statuses and propagate counterexamples through dependencies."""
    def revise(
        self,
        base: KnowledgeBase[P],
        hypotheses: Sequence[Hypothesis],
        reports: Sequence[ValidationReport],
    ) -> KnowledgeBase[P]:
        ...
