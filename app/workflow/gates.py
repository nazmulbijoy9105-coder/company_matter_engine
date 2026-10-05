"""Gates. Analysis gates can be passed with a recorded override (D5); only release is a hard stop.
OUT_OF_SCOPE can only be overridden by a LAWYER with a reason (D2)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from app.core.errors import GateBlocked
from app.domain.states import Maintainability, ScopeOutcome
from app.engines.jurisdiction_engine import ScopeResult
from app.engines.maintainability_engine import MaintainabilityResult
from app.workflow.state_machine import Workflow


@dataclass
class GateDecision:
    status: str                 # PASS | OVERRIDE_REQUIRED
    needs_lawyer: bool = False
    reasons: list[str] | None = None


def scope_gate(scope: ScopeResult) -> GateDecision:
    if scope.outcome == ScopeOutcome.IN_SCOPE_CANDIDATE:
        return GateDecision("PASS")
    return GateDecision("OVERRIDE_REQUIRED", needs_lawyer=scope.outcome == ScopeOutcome.OUT_OF_SCOPE,
                        reasons=scope.reasons)


def maintainability_gate(m: MaintainabilityResult) -> GateDecision:
    if m.gate == Maintainability.MAINTAINABLE:
        return GateDecision("PASS")
    return GateDecision("OVERRIDE_REQUIRED", reasons=[m.gate.value])


def advance_through_gate(wf: Workflow, to_state: str, decision: GateDecision, actor: str,
                         override_reason: Optional[str] = None, override_role: Optional[str] = None) -> None:
    if decision.status == "OVERRIDE_REQUIRED":
        if not override_reason:
            raise GateBlocked(f"gate not passed ({decision.reasons}); override_reason required")
        if decision.needs_lawyer and override_role != "LAWYER":
            raise GateBlocked("OUT_OF_SCOPE can only be overridden by a LAWYER")
    wf.advance(to_state, actor, override_reason, override_role)
