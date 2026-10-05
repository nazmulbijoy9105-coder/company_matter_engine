"""Maintainability gate (stage 5): statutory rule sets + limitation, per invoked hook."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.domain.matter import Matter
from app.domain.states import EvalState, Maintainability, combine_all, to_maintainability
from app.engines import limitation_engine
from app.engines.limitation_engine import LimitationResult
from app.engines.statutory_engine import RuleSetResult, evaluate_rule_set
from app.evidence.fact_mapping import lookup
from app.legal.rules.rulebook import RuleBook


@dataclass
class MaintainabilityResult:
    state: EvalState
    gate: Maintainability
    rule_sets: list[RuleSetResult] = field(default_factory=list)
    limitation: list[LimitationResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def unverified_rule_sets(self) -> list[str]:
        return [r.rule_set_id for r in self.rule_sets if r.unverified]


def evaluate(matter: Matter, book: Optional[RuleBook] = None) -> MaintainabilityResult:
    book = book or RuleBook.load()
    hooks = book.hooks()
    rs_by_hook: dict[str, list[str]] = {}
    for rsid, rs in book.maintainability["rule_sets"].items():
        rs_by_hook.setdefault(rs["hook"], []).append(rsid)
    lim_by_hook = {r["hook"]: r for r in book.limitation["rules"]}

    rule_sets: list[RuleSetResult] = []
    limitation: list[LimitationResult] = []
    notes: list[str] = []

    accrual = lookup(matter.facts, "limitation.accrual_date")
    filing = lookup(matter.facts, "limitation.filing_date")
    excl = lookup(matter.facts, "limitation.exclusion_days")
    exclusion_days = int(excl.value) if excl.state == "FOUND" and str(excl.value).isdigit() else 0

    for h in matter.invoked_hooks:
        hook = hooks.get(h)
        if hook is None:
            notes.append(f"UNREGISTERED_HOOK:{h}")
            continue
        if hook.get("covered_by"):
            notes.append(f"{h}_covered_by_{hook['covered_by']}")
            continue
        for rsid in rs_by_hook.get(h, []):
            rule_sets.append(evaluate_rule_set(rsid, matter, book))
        if h not in rs_by_hook:
            notes.append(f"no_rule_set_for_hook:{h}")
            rule_sets.append(RuleSetResult("NONE:" + h, h, EvalState.UNKNOWN, "PENDING",
                                           reasons=["no_rule_set_for_hook"]))
        lr = lim_by_hook.get(h)
        if lr is None:
            limitation.append(LimitationResult("NONE:" + h, EvalState.UNKNOWN, ["no_limitation_rule_for_hook"]))
        else:
            acc = accrual.value if accrual.state == "FOUND" else None
            fil = filing.value if filing.state == "FOUND" else None
            limitation.append(limitation_engine.evaluate(lr, acc, fil, exclusion_days))

    overall = combine_all([r.state for r in rule_sets] + [l.state for l in limitation])
    return MaintainabilityResult(overall, to_maintainability(overall), rule_sets, limitation, notes)
