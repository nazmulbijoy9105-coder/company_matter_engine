"""Resolve a predicate to a usable value. Only VERIFIED facts count (D6)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterable

from app.domain.fact import Fact, FactStatus


@dataclass
class FactLookup:
    state: str                 # FOUND | MISSING | UNVERIFIED_ONLY | CONFLICT | DISPUTED
    value: Any = None
    fact_ids: list[str] = field(default_factory=list)


def lookup(facts: Iterable[Fact], predicate: str) -> FactLookup:
    rel = [f for f in facts if f.predicate == predicate and f.status != FactStatus.REJECTED]
    if not rel:
        return FactLookup("MISSING")
    ids = [f.fact_id for f in rel]
    if any(f.status == FactStatus.DISPUTED for f in rel):
        return FactLookup("DISPUTED", fact_ids=ids)
    verified = [f for f in rel if f.status == FactStatus.VERIFIED]
    if not verified:
        return FactLookup("UNVERIFIED_ONLY", fact_ids=ids)
    values = {_norm(f.object) for f in verified}
    if len(values) > 1:
        return FactLookup("CONFLICT", fact_ids=[f.fact_id for f in verified])
    return FactLookup("FOUND", value=verified[0].object, fact_ids=[f.fact_id for f in verified])


def _norm(v: Any) -> str:
    return str(v).strip().lower()


def norm_equal(a: Any, b: Any) -> bool:
    return _norm(a) == _norm(b)
