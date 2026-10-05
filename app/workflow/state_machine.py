"""Matter state machine. No skipping steps; PRECEDENT_RESEARCH is skipped only in LAW_ONLY mode."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.core.errors import GateBlocked

STATES = [
    "INTAKE", "FACT_COLLECTION", "EVIDENCE_REVIEW", "CLASSIFIED", "JURISDICTION_CHECK",
    "MAINTAINABILITY_CHECK", "LEGAL_ANALYSIS", "PRECEDENT_RESEARCH", "ISSUE_FORMULATION",
    "ARGUMENT_ANALYSIS", "RELIEF_ANALYSIS", "DRAFTING", "LAWYER_REVIEW", "APPROVED", "FROZEN",
]


def next_state(current: str, mode: str) -> Optional[str]:
    i = STATES.index(current)
    if i == len(STATES) - 1:
        return None
    nxt = STATES[i + 1]
    if nxt == "PRECEDENT_RESEARCH" and mode == "LAW_ONLY":
        nxt = STATES[i + 2]
    return nxt


@dataclass
class Transition:
    from_state: str
    to_state: str
    actor: str
    override_reason: Optional[str] = None
    override_role: Optional[str] = None


@dataclass
class Workflow:
    matter_id: str
    mode: str = "LAW_ONLY"
    state: str = "INTAKE"
    history: list[Transition] = field(default_factory=list)

    def advance(self, to_state: str, actor: str, override_reason: Optional[str] = None,
                override_role: Optional[str] = None) -> None:
        expected = next_state(self.state, self.mode)
        if to_state != expected:
            raise GateBlocked(f"cannot go {self.state} -> {to_state}; next allowed is {expected}")
        self.history.append(Transition(self.state, to_state, actor, override_reason, override_role))
        self.state = to_state
