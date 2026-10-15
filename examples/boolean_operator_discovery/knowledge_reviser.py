"""Revise the knowledge base: register corroborated programs, refute on counterexample.

A program only becomes *active knowledge* after its validation report is
``CORROBORATED``. A ``REFUTED`` report turns any active knowledge sharing the
same hypothesis into ``REFUTED`` (revision by invalidation), preserving the
provenance links (execution ids, validation report ids, dependencies).
"""

from collections.abc import Sequence
from dataclasses import replace

from epistemic_sdk import (
    Hypothesis,
    Knowledge,
    KnowledgeBase,
    KnowledgeStatus,
    ProgramM1,
    ValidationReport,
    ValidationStatus,
)


class BooleanKnowledgeReviser:
    """Register/refute knowledge from validation reports."""

    def revise(
        self,
        base: KnowledgeBase[ProgramM1],
        hypotheses: Sequence[Hypothesis],
        reports: Sequence[ValidationReport],
    ) -> KnowledgeBase[ProgramM1]:
        report_by_hypothesis = {report.hypothesis_id: report for report in reports}
        entries: list[Knowledge[ProgramM1]] = list(base.entries)

        for hypothesis in hypotheses:
            report = report_by_hypothesis.get(hypothesis.id)
            if report is None:
                continue

            if report.status == ValidationStatus.CORROBORATED:
                if all(entry.hypothesis_id != hypothesis.id for entry in entries):
                    entries.append(
                        Knowledge(
                            id=f"K_{hypothesis.id}",
                            program=hypothesis.program,
                            hypothesis_id=hypothesis.id,
                            execution_ids=(report.execution_id,),
                            validation_report_ids=(report.id,),
                            dependency_ids=hypothesis.supporting_belief_ids,
                            status=KnowledgeStatus.ACTIVE,
                        )
                    )
            elif report.status == ValidationStatus.REFUTED:
                entries = [
                    replace(entry, status=KnowledgeStatus.REFUTED)
                    if entry.hypothesis_id == hypothesis.id
                    and entry.status == KnowledgeStatus.ACTIVE
                    else entry
                    for entry in entries
                ]

        return KnowledgeBase(entries=tuple(entries), version=base.version + 1)
