from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _matter():
    r = client.post("/matters", json={"invoked_hooks": ["HOOK-CA-233", "HOOK-CA-195"],
                                      "requested_relief": ["REM-005"]})
    assert r.status_code == 200
    return r.json()["matter_id"]


def test_ai_fact_cannot_be_verified_via_api():
    mid = _matter()
    fid = client.post(f"/matters/{mid}/facts", json={"predicate": "applicant.is_member", "object": True,
                                                     "created_by": "extractor", "created_by_kind": "AI"}).json()["fact_id"]
    assert client.post(f"/matters/{mid}/facts/{fid}/verify", json={"reviewer": "model", "actor_kind": "AI"}).status_code == 403
    ok = client.post(f"/matters/{mid}/facts/{fid}/verify", json={"reviewer": "adv. x", "actor_kind": "HUMAN"})
    assert ok.status_code == 200 and ok.json()["status"] == "VERIFIED"


def test_analysis_records_snapshot_and_log_verifies():
    mid = _matter()
    r = client.post(f"/matters/{mid}/analysis")
    assert r.status_code == 200
    body = r.json()
    assert body["result"]["scope"]["outcome"] == "IN_SCOPE_CANDIDATE"
    assert body["result"]["scope"]["unverified_sources"]
    assert client.get("/audit/verify").json()["ok"] is True


def test_stub_routes_say_501_not_fake_success():
    mid = _matter()
    assert client.get(f"/matters/{mid}/drafting").status_code == 501


def test_health_reports_versions():
    assert client.get("/health").json()["versions"]["engine"] == "0.1.0"
