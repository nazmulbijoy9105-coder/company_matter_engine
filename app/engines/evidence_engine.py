"""Evidence coverage: which required evidence types are not yet on file for the invoked hooks."""
from __future__ import annotations
from typing import Optional

from app.domain.matter import Matter
from app.legal.rules.rulebook import RuleBook


def coverage(matter: Matter, book: Optional[RuleBook] = None) -> dict[str, dict]:
    book = book or RuleBook.load()
    have = {d.evidence_type_id for d in matter.documents}
    out = {}
    for h in matter.invoked_hooks:
        req = book.evidence["required_evidence"].get(h)
        if req is None:
            out[h] = {"required": None, "missing": None, "note": "no_evidence_requirements_authored"}
            continue
        out[h] = {"required": req, "missing": [e for e in req if e not in have]}
    return out
