from __future__ import annotations
from dataclasses import dataclass, field

from app.domain.states import EvalState


@dataclass
class Issue:
    issue_id: str
    type_id: str
    question: str
    state: EvalState
    element_ids: list[str] = field(default_factory=list)
    fact_ids: list[str] = field(default_factory=list)
    rule_set_ids: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
