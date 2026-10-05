"""Orders by court tier only. Deliberately NOT a numeric authority score (blueprint s.13):
relevance, ratio fit and treatment need a lawyer's judgment."""
from __future__ import annotations

from app.precedent.registry import PrecedentRecord

TIERS = ["Appellate Division", "High Court Division", "Other persuasive"]


def tier(r: PrecedentRecord) -> int:
    c = (r.court or "") + " " + (r.division or "")
    if "Appellate" in c:
        return 0
    if "High Court" in c:
        return 1
    return 2


def order_by_tier(records: list[PrecedentRecord]) -> list[PrecedentRecord]:
    return sorted(records, key=tier)
