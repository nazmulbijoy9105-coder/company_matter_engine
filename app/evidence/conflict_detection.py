from __future__ import annotations
from collections import defaultdict
from typing import Iterable

from app.domain.fact import Fact, FactStatus
from app.evidence.fact_mapping import _norm


def find_conflicts(facts: Iterable[Fact]) -> dict[str, list[str]]:
    """predicate -> fact_ids, for predicates with differing VERIFIED values."""
    by_pred: dict[str, list[Fact]] = defaultdict(list)
    for f in facts:
        if f.status == FactStatus.VERIFIED:
            by_pred[f.predicate].append(f)
    return {p: [f.fact_id for f in fs] for p, fs in by_pred.items()
            if len({_norm(f.object) for f in fs}) > 1}
