"""Decision provenance: which rules/facts a conclusion relied on, and the verification debt."""
from __future__ import annotations

from app.engines.jurisdiction_engine import ScopeResult
from app.engines.maintainability_engine import MaintainabilityResult


def provenance(scope: ScopeResult, maint: MaintainabilityResult) -> dict:
    return {
        "scope_outcome": scope.outcome.value,
        "scope_unverified_sources": scope.unverified_sources,
        "hooks_matched": scope.hooks_matched,
        "rule_sets": [
            {"id": r.rule_set_id, "state": r.state.value, "authoring_status": r.authoring_status,
             "fact_ids": sorted({f for e in r.elements for f in e.fact_ids})}
            for r in maint.rule_sets
        ],
        "unverified_rule_sets": maint.unverified_rule_sets,
    }
