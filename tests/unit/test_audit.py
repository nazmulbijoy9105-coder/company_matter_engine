import copy

from app.audit.audit_log import AuditLog
from app.audit.integrity import verify_snapshot
from app.audit.snapshot import build_snapshot
from app.domain.matter import Matter


def test_chain_verifies_and_detects_tamper():
    log = AuditLog()
    for i in range(4):
        log.append("M1", "a", "ACT", {"i": i}, ts="2026-10-06T00:00:00+00:00")
    assert log.verify() == (True, None)
    log.events[2].payload["i"] = 99
    assert log.verify() == (False, 2)


def test_chain_detects_deleted_event():
    log = AuditLog()
    for i in range(3):
        log.append("M1", "a", "ACT", {"i": i}, ts="t")
    del log.events[1]
    ok, bad = log.verify()
    assert not ok


def test_snapshot_tamper_detected():
    m = Matter(matter_id="M1")
    snap = build_snapshot(m, {"x": 1}, "actor", versions={"engine": "t"}, ts="t")
    assert verify_snapshot(snap) == []
    bad = copy.deepcopy(snap)
    bad["outputs"]["x"] = 2
    assert "output_hash_mismatch" in verify_snapshot(bad)


def test_snapshot_input_hash_changes_with_input():
    a = build_snapshot(Matter(matter_id="M1"), {}, "a", versions={}, ts="t")
    b = build_snapshot(Matter(matter_id="M1", invoked_hooks=["HOOK-CA-43"]), {}, "a", versions={}, ts="t")
    assert a["input_hash"] != b["input_hash"]
