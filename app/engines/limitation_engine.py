"""Limitation (D7): no automatic date fallback. Missing input => UNKNOWN, never 'within time'.
Condonation / equitable delay are NOT assumed; an out-of-time result is NOT_SATISFIED and the
lawyer decides whether any condonation route exists."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from app.domain.states import EvalState


@dataclass
class LimitationResult:
    rule_id: str
    state: EvalState
    reasons: list[str] = field(default_factory=list)
    deadline: Optional[str] = None


def _parse(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(str(s))
    except ValueError:
        return None


def evaluate(rule: dict, accrual: Optional[str], filing: Optional[str], exclusion_days: int = 0) -> LimitationResult:
    rid = rule["id"]
    if rule.get("authoring_status") == "PENDING" or rule.get("period_days") is None:
        return LimitationResult(rid, EvalState.UNKNOWN, ["limitation_rule_pending_authoring"])
    a, f = _parse(accrual), _parse(filing)
    reasons = []
    if a is None:
        reasons.append("missing_or_invalid_accrual_date")
    if f is None:
        reasons.append("missing_or_invalid_filing_date")
    if reasons:
        return LimitationResult(rid, EvalState.UNKNOWN, reasons)
    deadline = a + timedelta(days=int(rule["period_days"]) + int(exclusion_days))
    if f <= deadline:
        return LimitationResult(rid, EvalState.SATISFIED, deadline=deadline.isoformat())
    return LimitationResult(rid, EvalState.NOT_SATISFIED,
                            ["out_of_time:condonation_not_assumed"], deadline.isoformat())
