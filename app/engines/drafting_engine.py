"""Drafting guard (stage 11). Every paragraph carries provenance; unverified precedent cannot be
cited as authority; unverified/absent facts cannot support an assertion. Templates live in
app/drafting/ (stubs until lawyer-authored)."""
from __future__ import annotations
from dataclasses import dataclass, field

from app.domain.fact import Fact, FactStatus
from app.precedent.registry import PrecedentRegistry


@dataclass
class DraftParagraph:
    paragraph_id: str
    text: str
    fact_ids: list[str] = field(default_factory=list)
    rule_set_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    precedent_ids: list[str] = field(default_factory=list)


def validate_draft(paragraphs: list[DraftParagraph], facts: list[Fact], reg: PrecedentRegistry) -> list[str]:
    """Returns violations; empty list means the draft may go to lawyer review."""
    fact_status = {f.fact_id: f.status for f in facts}
    v = []
    for p in paragraphs:
        if not (p.fact_ids or p.rule_set_ids or p.precedent_ids):
            v.append(f"{p.paragraph_id}:no_provenance")
        for fid in p.fact_ids:
            if fact_status.get(fid) != FactStatus.VERIFIED:
                v.append(f"{p.paragraph_id}:fact_not_verified:{fid}")
        for pid in p.precedent_ids:
            if not reg.citable(pid):
                v.append(f"{p.paragraph_id}:unverified_precedent:{pid}")
    return v
