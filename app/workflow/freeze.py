"""Release / freeze. The ONLY hard stop (D5): release requires lawyer approval of every paragraph,
a clean draft validation, and no unwaived verification debt."""
from __future__ import annotations
from typing import Any

from app.audit.audit_log import AuditLog
from app.audit.snapshot import build_snapshot
from app.core.errors import GateBlocked
from app.domain.matter import Matter
from app.engines.drafting_engine import DraftParagraph, validate_draft
from app.precedent.registry import PrecedentRegistry
from app.workflow.review import ReviewLedger


def release_blockers(matter: Matter, paragraphs: list[DraftParagraph], ledger: ReviewLedger,
                     reg: PrecedentRegistry, unverified_sources: list[str]) -> list[str]:
    blockers = []
    blockers += validate_draft(paragraphs, matter.facts, reg)
    pids = [p.paragraph_id for p in paragraphs]
    if not pids:
        blockers.append("empty_draft")
    elif not ledger.approved(pids):
        blockers.append("paragraphs_not_all_lawyer_approved")
    blockers += [f"unwaived_unverified_source:{s}" for s in unverified_sources if not ledger.waived(s)]
    return blockers


def release_and_freeze(matter: Matter, paragraphs: list[DraftParagraph], ledger: ReviewLedger,
                       reg: PrecedentRegistry, unverified_sources: list[str], outputs: dict[str, Any],
                       log: AuditLog, actor: str, reviewer: str) -> dict:
    blockers = release_blockers(matter, paragraphs, ledger, reg, unverified_sources)
    if blockers:
        raise GateBlocked(f"release blocked: {blockers}")
    snap = build_snapshot(matter, outputs, actor, reviewer)
    log.append(matter.matter_id, actor, "RELEASED_FROZEN", {"snapshot_hash": snap["snapshot_hash"]})
    return snap
