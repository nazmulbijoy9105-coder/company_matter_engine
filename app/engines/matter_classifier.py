"""Multi-label classifier (stage 3). Derives candidate matter types from invoked hooks.
It never silently picks a primary when candidates tie: that is a reviewer choice."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.domain.matter import Matter
from app.legal.corpus.registries import matter_registry


@dataclass
class Classification:
    candidates: list[str] = field(default_factory=list)
    primary: Optional[str] = None
    needs_reviewer_choice: bool = False
    civil_boundary_risk: bool = False
    notes: list[str] = field(default_factory=list)


def classify(matter: Matter) -> Classification:
    reg = matter_registry()
    invoked = set(matter.invoked_hooks)
    scored = []
    for mid, m in reg.items():
        hooks = set(m.get("hooks", []))
        if hooks and hooks & invoked:
            scored.append((len(hooks & invoked) / len(hooks), mid))
    if not scored:
        return Classification(notes=["no_matter_type_matches_invoked_hooks"])
    best = max(s for s, _ in scored)
    cands = sorted(mid for _, mid in scored)
    top = sorted(mid for s, mid in scored if s == best)
    out = Classification(candidates=cands)
    out.civil_boundary_risk = any(reg[m].get("civil_boundary_risk") for m in cands)

    chosen = [m for m in matter.proposed_matter_types if m in cands]
    invalid = [m for m in matter.proposed_matter_types if m not in cands]
    if invalid:
        out.notes.append(f"proposed_types_not_supported_by_invoked_hooks:{invalid}")
    if chosen:
        out.primary = chosen[0]
    elif len(top) == 1:
        out.primary = top[0]
    else:
        out.needs_reviewer_choice = True
        out.notes.append(f"primary_ambiguous_between:{top}")
    return out
