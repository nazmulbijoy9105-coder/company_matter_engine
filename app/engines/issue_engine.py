"""Issue formulation (stage 9a): issue states are aggregated from element/limitation/relief results."""
from __future__ import annotations

from app.domain.issue import Issue
from app.domain.states import EvalState, ReliefAvailability, ScopeOutcome, combine_all
from app.engines.jurisdiction_engine import ScopeResult
from app.engines.maintainability_engine import MaintainabilityResult
from app.engines.relief_engine import ReliefResult
from app.legal.rules.loader import taxonomy

_SCOPE_STATE = {
    ScopeOutcome.IN_SCOPE_CANDIDATE: EvalState.SATISFIED,
    ScopeOutcome.OUT_OF_SCOPE: EvalState.NOT_SATISFIED,
    ScopeOutcome.UNCERTAIN_LAWYER_REVIEW: EvalState.REQUIRES_LAWYER_JUDGMENT,
}
_RELIEF_STATE = {
    ReliefAvailability.AVAILABLE: EvalState.SATISFIED,
    ReliefAvailability.CONDITIONALLY_AVAILABLE: EvalState.REQUIRES_LAWYER_JUDGMENT,
    ReliefAvailability.NOT_ESTABLISHED: EvalState.UNKNOWN,
    ReliefAvailability.NOT_AVAILABLE: EvalState.NOT_SATISFIED,
}


def build_issues(scope: ScopeResult, maint: MaintainabilityResult, relief: list[ReliefResult]) -> list[Issue]:
    questions = {i["id"]: i["question"] for i in taxonomy("issue_types")["issue_types"]}
    issues: list[Issue] = []

    def add(type_id, state, element_ids=(), fact_ids=(), rs=(), reasons=()):
        issues.append(Issue(type_id, type_id, questions[type_id], state, list(element_ids),
                            list(fact_ids), list(rs), list(reasons)))

    for tid in ("ISSUE-STANDING", "ISSUE-SCOPE", "ISSUE-PREREQ", "ISSUE-ACT"):
        els = [(r.rule_set_id, e) for r in maint.rule_sets for e in r.elements if e.issue == tid]
        states = [e.state for _, e in els]
        if tid == "ISSUE-SCOPE":
            states.append(_SCOPE_STATE[scope.outcome])
        if not states:
            add(tid, EvalState.UNKNOWN, reasons=["no_authored_elements"])
            continue
        add(tid, combine_all(states), [e.element_id for _, e in els],
            [f for _, e in els for f in e.fact_ids], sorted({rs for rs, _ in els}))

    lim_states = [l.state for l in maint.limitation]
    add("ISSUE-LIMITATION", combine_all(lim_states) if lim_states else EvalState.UNKNOWN,
        reasons=[x for l in maint.limitation for x in l.reasons])

    if relief:
        add("ISSUE-RELIEF", combine_all(_RELIEF_STATE[r.availability] for r in relief),
            reasons=[f"{r.remedy_id}:{r.availability.value}" for r in relief])
    else:
        add("ISSUE-RELIEF", EvalState.UNKNOWN, reasons=["no_relief_requested"])
    return issues
