"""Legal evaluation (stage 7): Fact x Rule x Element -> EvalState.
Evaluative tests are never auto-resolved (D3). PENDING rule sets evaluate to UNKNOWN."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.domain.matter import Matter
from app.domain.states import EvalState, combine_all
from app.evidence.fact_mapping import lookup, norm_equal
from app.legal.rules.rulebook import RuleBook


@dataclass
class ElementResult:
    element_id: str
    state: EvalState
    label: str = ""
    issue: Optional[str] = None
    fact_ids: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    factors: list[str] = field(default_factory=list)
    evidence_types: list[str] = field(default_factory=list)
    relies_on_unverified_value: bool = False


@dataclass
class RuleSetResult:
    rule_set_id: str
    hook: str
    state: EvalState
    authoring_status: str
    elements: list[ElementResult] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    @property
    def unverified(self) -> bool:
        return self.authoring_status != "VERIFIED" or any(e.relies_on_unverified_value for e in self.elements)


def _eval_element(el: dict, matter: Matter) -> ElementResult:
    base = dict(element_id=el["id"], label=el.get("label", ""), issue=el.get("issue"),
                evidence_types=el.get("evidence", []))
    t = el["type"]
    if t == "JUDGMENT":
        return ElementResult(state=EvalState.REQUIRES_LAWYER_JUDGMENT, factors=el.get("factors", []),
                             reasons=["evaluative_test_not_auto_resolved"], **base)

    fl = lookup(matter.facts, el["predicate"])
    if fl.state in ("MISSING", "UNVERIFIED_ONLY"):
        return ElementResult(state=EvalState.UNKNOWN, fact_ids=fl.fact_ids,
                             reasons=[f"fact_{fl.state.lower()}:{el['predicate']}"], **base)
    if fl.state in ("CONFLICT", "DISPUTED"):
        return ElementResult(state=EvalState.DISPUTED, fact_ids=fl.fact_ids,
                             reasons=[f"fact_{fl.state.lower()}:{el['predicate']}"], **base)

    if t == "FACT_EXISTS":
        ok = norm_equal(fl.value, el["expected"])
        return ElementResult(state=EvalState.SATISFIED if ok else EvalState.NOT_SATISFIED,
                             fact_ids=fl.fact_ids, **base)
    if t == "THRESHOLD_GTE":
        try:
            ok = float(fl.value) >= float(el["value"])
        except (TypeError, ValueError):
            return ElementResult(state=EvalState.UNKNOWN, fact_ids=fl.fact_ids,
                                 reasons=[f"non_numeric_fact:{el['predicate']}"], **base)
        return ElementResult(state=EvalState.SATISFIED if ok else EvalState.NOT_SATISFIED,
                             fact_ids=fl.fact_ids,
                             relies_on_unverified_value=el.get("value_status") != "VERIFIED", **base)
    raise ValueError(f"unknown element type {t}")


def evaluate_rule_set(rule_set_id: str, matter: Matter, book: Optional[RuleBook] = None) -> RuleSetResult:
    book = book or RuleBook.load()
    rs = book.maintainability["rule_sets"][rule_set_id]
    status = rs["authoring_status"]
    if rs["hook"] not in matter.invoked_hooks:
        return RuleSetResult(rule_set_id, rs["hook"], EvalState.NOT_APPLICABLE, status,
                             reasons=["hook_not_invoked"])
    if status == "PENDING" or not rs["elements"]:
        return RuleSetResult(rule_set_id, rs["hook"], EvalState.UNKNOWN, status,
                             reasons=["rule_set_pending_authoring"])
    elements = [_eval_element(e, matter) for e in rs["elements"]]
    return RuleSetResult(rule_set_id, rs["hook"], combine_all(e.state for e in elements), status, elements)
