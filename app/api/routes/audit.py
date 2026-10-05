from fastapi import APIRouter

from app.api.dependencies import AUDIT

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/verify")
def verify_log():
    ok, bad = AUDIT.verify()
    return {"ok": ok, "first_bad_seq": bad, "events": len(AUDIT.events)}
