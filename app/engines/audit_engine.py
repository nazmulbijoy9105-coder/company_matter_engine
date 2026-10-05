"""Audit orchestration: snapshot + log append in one call."""
from __future__ import annotations
from typing import Any, Optional

from app.audit.audit_log import AuditLog
from app.audit.snapshot import build_snapshot
from app.domain.matter import Matter


def record_analysis(log: AuditLog, matter: Matter, outputs: dict[str, Any], actor: str,
                    reviewer: Optional[str] = None) -> dict:
    snap = build_snapshot(matter, outputs, actor, reviewer)
    log.append(matter.matter_id, actor, "ANALYSIS_SNAPSHOT",
               {"snapshot_hash": snap["snapshot_hash"], "output_hash": snap["output_hash"]})
    return snap
