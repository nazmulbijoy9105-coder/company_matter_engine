"""Relief (stage 10). The engine never invents relief: a remedy is only as available as the
authored rule sets it depends on."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.domain.matter import Matter
from app.domain.states import EvalState, ReliefAvailability, ScopeOutcome
from app.engines.jurisdiction_engine import ScopeResult
from app.engines.maintainability_engine import MaintainabilityResult
from app.legal.corpus.registries import remedy_registry
from app.legal.rules.rulebook import RuleBook


@dataclass
class ReliefResult:
    remedy_id: str
    availability: ReliefAvailability
    reasons: list[str] = field(default_factory=list)


def evaluate(matter: Matter, scope: ScopeResult, maint: MaintainabilityResult,
             book: Optional[RuleBook] = None) -> list[ReliefResult]:
    book = book or RuleBook.load()
    reg = remedy_registry()
    by_rs = {r.rule_set_id: r for r in maint.rule_sets}
    out = []
    for rid in matter.requested_relief:
        if scope.outcome == ScopeOutcome.OUT_OF_SCOPE:
            out.append(ReliefResult(rid, ReliefAvailability.NOT_AVAILABLE, ["scope_gate_not_passed"]))
            continue
        if not reg.get(rid, {}).get("company_bench_remedy", False):
            out.append(ReliefResult(rid, ReliefAvailability.NOT_AVAILABLE, ["not_a_company_bench_remedy"]))
            continue
        req = book.relief["remedies"].get(rid, {}).get("requires", [])
        evaluated = [by_rs[r] for r in req if r in by_rs and by_rs[r].state != EvalState.NOT_APPLICABLE]
        if not req or not evaluated:
            out.append(ReliefResult(rid, ReliefAvailability.NOT_ESTABLISHED, ["no_authored_requirements_evaluated"]))
        elif any(r.state == EvalState.NOT_SATISFIED for r in evaluated):
            out.append(ReliefResult(rid, ReliefAvailability.NOT_AVAILABLE,
                                    [f"unsatisfied:{r.rule_set_id}" for r in evaluated if r.state == EvalState.NOT_SATISFIED]))
        elif any(r.reasons and "rule_set_pending_authoring" in r.reasons for r in evaluated):
            out.append(ReliefResult(rid, ReliefAvailability.NOT_ESTABLISHED, ["rule_set_pending_authoring"]))
        elif all(r.state == EvalState.SATISFIED for r in evaluated):
            out.append(ReliefResult(rid, ReliefAvailability.AVAILABLE))
        else:
            out.append(ReliefResult(rid, ReliefAvailability.CONDITIONALLY_AVAILABLE,
                                    [f"{r.rule_set_id}:{r.state.value}" for r in evaluated if r.state != EvalState.SATISFIED]))
    return out
