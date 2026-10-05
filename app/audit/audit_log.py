"""Append-only, hash-chained audit log: tamper-evident, not re-derivable (D8)."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.audit.hashes import sha256_hex

GENESIS = "0" * 64


@dataclass
class AuditEvent:
    seq: int
    matter_id: str
    actor: str
    action: str
    payload: dict
    ts: str
    prev_hash: str
    hash: str = ""


class AuditLog:
    def __init__(self):
        self.events: list[AuditEvent] = []

    def append(self, matter_id: str, actor: str, action: str, payload: dict[str, Any] | None = None,
               ts: str | None = None) -> AuditEvent:
        prev = self.events[-1].hash if self.events else GENESIS
        ev = AuditEvent(len(self.events), matter_id, actor, action, payload or {},
                        ts or datetime.now(timezone.utc).isoformat(), prev)
        ev.hash = _event_hash(ev)
        self.events.append(ev)
        return ev

    def verify(self) -> tuple[bool, int | None]:
        """Returns (ok, first_bad_seq)."""
        prev = GENESIS
        for ev in self.events:
            if ev.prev_hash != prev or ev.hash != _event_hash(ev):
                return False, ev.seq
            prev = ev.hash
        return True, None


def _event_hash(ev: AuditEvent) -> str:
    return sha256_hex({"seq": ev.seq, "matter_id": ev.matter_id, "actor": ev.actor, "action": ev.action,
                       "payload": ev.payload, "ts": ev.ts, "prev_hash": ev.prev_hash})
