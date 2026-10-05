import json
from fastapi import APIRouter

from app.api.dependencies import AUDIT, get_matter
from app.audit.hashes import canonical_json
from app.engines import audit_engine, pipeline

router = APIRouter(prefix="/matters/{matter_id}/analysis", tags=["analysis"])


@router.post("")
def run_analysis(matter_id: str, actor: str = "api"):
    m = get_matter(matter_id)
    res = pipeline.run(m)
    out = json.loads(canonical_json(res))
    snap = audit_engine.record_analysis(AUDIT, m, out, actor)
    return {"result": out, "snapshot_hash": snap["snapshot_hash"],
            "note": "Rules and provisions are UNVERIFIED_FROM_BLUEPRINT; not releasable without lawyer waiver."}
