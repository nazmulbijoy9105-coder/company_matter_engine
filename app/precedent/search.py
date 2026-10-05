from __future__ import annotations

from app.precedent.registry import PrecedentRegistry, PrecedentRecord, VERIFIED


def by_provision(reg: PrecedentRegistry, provision_id: str, verified_only: bool = True) -> list[PrecedentRecord]:
    out = [r for r in reg.all() if provision_id in r.provisions]
    return [r for r in out if r.status == VERIFIED] if verified_only else out
