"""Argument skeletons (stage 9b)."""
from __future__ import annotations

from app.domain.argument import ArgumentNode
from app.engines.maintainability_engine import MaintainabilityResult


def skeletons(maint: MaintainabilityResult) -> list[ArgumentNode]:
    out = []
    for rs in maint.rule_sets:
        for el in rs.elements:
            out.append(ArgumentNode(
                issue_id=el.issue or "ISSUE-UNASSIGNED", rule_set_id=rs.rule_set_id,
                element_id=el.element_id, fact_ids=list(el.fact_ids),
                evidence_types=list(el.evidence_types), conclusion_state=el.state.value))
    return out
