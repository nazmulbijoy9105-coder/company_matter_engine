"""Lawyer review ledger: every draft paragraph must be individually approved by a LAWYER."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.errors import GateBlocked


@dataclass
class ReviewRecord:
    item_id: str
    reviewer: str
    role: str
    decision: str            # APPROVE | REJECT
    note: str = ""
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReviewLedger:
    def __init__(self):
        self.records: list[ReviewRecord] = []
        self.waivers: list[ReviewRecord] = []   # verification-debt waivers (item_id = rules source)

    def review(self, item_id: str, reviewer: str, role: str, decision: str, note: str = "") -> None:
        if role != "LAWYER":
            raise GateBlocked("only a LAWYER can review")
        if decision not in ("APPROVE", "REJECT"):
            raise ValueError("decision must be APPROVE or REJECT")
        self.records.append(ReviewRecord(item_id, reviewer, role, decision, note))

    def waive_unverified(self, source: str, reviewer: str, role: str, reason: str) -> None:
        if role != "LAWYER" or not reason:
            raise GateBlocked("waiver needs a LAWYER and a reason")
        self.waivers.append(ReviewRecord(source, reviewer, role, "WAIVE", reason))

    def latest(self, item_id: str) -> str | None:
        for r in reversed(self.records):
            if r.item_id == item_id:
                return r.decision
        return None

    def approved(self, item_ids: list[str]) -> bool:
        return all(self.latest(i) == "APPROVE" for i in item_ids)

    def waived(self, source: str) -> bool:
        return any(w.item_id == source for w in self.waivers)
