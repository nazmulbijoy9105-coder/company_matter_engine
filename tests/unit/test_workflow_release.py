import pytest

from app.audit.audit_log import AuditLog
from app.core.errors import GateBlocked, VerificationError
from app.domain.fact import Fact, FactStatus
from app.domain.matter import Matter
from app.engines import jurisdiction_engine
from app.engines.drafting_engine import DraftParagraph
from app.precedent.registry import PrecedentRecord, PrecedentRegistry, VERIFIED
from app.workflow.freeze import release_and_freeze, release_blockers
from app.workflow.gates import advance_through_gate, scope_gate
from app.workflow.review import ReviewLedger
from app.workflow.state_machine import Workflow, next_state


def test_no_skipping_and_law_only_skips_precedent():
    wf = Workflow("M", mode="LAW_ONLY", state="LEGAL_ANALYSIS")
    with pytest.raises(GateBlocked):
        wf.advance("PRECEDENT_RESEARCH", "a")
    wf.advance("ISSUE_FORMULATION", "a")
    assert next_state("LEGAL_ANALYSIS", "LAW_PLUS_PRECEDENT") == "PRECEDENT_RESEARCH"
    with pytest.raises(GateBlocked):
        Workflow("M", state="INTAKE").advance("CLASSIFIED", "a")


def _out_of_scope():
    m = Matter(matter_id="M", requested_relief=["REM-900"], substance_flags=["recovery_of_money"])
    return jurisdiction_engine.screen(m)


def test_out_of_scope_needs_lawyer_override_with_reason():
    d = scope_gate(_out_of_scope())
    wf = Workflow("M", state="JURISDICTION_CHECK")
    with pytest.raises(GateBlocked):
        advance_through_gate(wf, "MAINTAINABILITY_CHECK", d, "a")
    with pytest.raises(GateBlocked):
        advance_through_gate(wf, "MAINTAINABILITY_CHECK", d, "a", "because", "INTAKE")
    advance_through_gate(wf, "MAINTAINABILITY_CHECK", d, "lawyer1", "forum confirmed with client", "LAWYER")
    assert wf.state == "MAINTAINABILITY_CHECK" and wf.history[-1].override_reason


def test_ai_cannot_verify_fact():
    f = Fact("F1", "M", "p", 1)
    with pytest.raises(VerificationError):
        f.verify("model", "AI")
    f.verify("adv. x", "HUMAN")
    assert f.status == FactStatus.VERIFIED


def _ready():
    f = Fact("F1", "M", "p", 1, status=FactStatus.VERIFIED)
    m = Matter(matter_id="M", facts=[f])
    paras = [DraftParagraph("P1", "text", fact_ids=["F1"])]
    return m, paras


def test_release_blocked_until_review_and_waiver():
    m, paras = _ready()
    reg, ledger = PrecedentRegistry(), ReviewLedger()
    unverified = ["rules/scope"]
    b = release_blockers(m, paras, ledger, reg, unverified)
    assert "paragraphs_not_all_lawyer_approved" in b and "unwaived_unverified_source:rules/scope" in b
    ledger.review("P1", "adv", "LAWYER", "APPROVE")
    ledger.waive_unverified("rules/scope", "adv", "LAWYER", "reviewed against statute text")
    assert release_blockers(m, paras, ledger, reg, unverified) == []
    snap = release_and_freeze(m, paras, ledger, reg, unverified, {"ok": 1}, AuditLog(), "sys", "adv")
    assert snap["reviewer"] == "adv"


def test_non_lawyer_cannot_review_or_waive():
    ledger = ReviewLedger()
    with pytest.raises(GateBlocked):
        ledger.review("P1", "clerk", "REVIEWER", "APPROVE")
    with pytest.raises(GateBlocked):
        ledger.waive_unverified("rules/scope", "clerk", "REVIEWER", "x")


def test_unverified_precedent_and_unverified_fact_block_release():
    m, _ = _ready()
    unverified_fact = Fact("F2", "M", "q", 1, status=FactStatus.PROPOSED)
    m.facts.append(unverified_fact)
    paras = [DraftParagraph("P1", "t", fact_ids=["F1", "F2"], precedent_ids=["PREC-X"])]
    ledger = ReviewLedger()
    ledger.review("P1", "adv", "LAWYER", "APPROVE")
    b = release_blockers(m, paras, ledger, PrecedentRegistry(), [])
    assert "P1:fact_not_verified:F2" in b and "P1:unverified_precedent:PREC-X" in b


def test_precedent_needs_every_verification_element():
    full = dict(precedent_id="P", court="High Court Division", division="Company Bench", case_number="X",
                text_sha256="ab", source_verified=True, case_number_verified=True, court_verified=True,
                text_verified=True, verified_by="adv", verified_on="2026-10-06")
    assert PrecedentRecord(**full).status == VERIFIED
    for key in ("source_verified", "case_number_verified", "court_verified", "text_verified"):
        assert PrecedentRecord(**{**full, key: False}).status != VERIFIED
    for key in ("case_number", "text_sha256", "verified_by"):
        assert PrecedentRecord(**{**full, key: None}).status != VERIFIED
    assert not PrecedentRegistry().citable("anything")
