from dataclasses import asdict
from fastapi import APIRouter

from app.api.dependencies import get_matter
from app.audit.hashes import canonical_json
from app.engines import jurisdiction_engine

import json

router = APIRouter(prefix="/matters/{matter_id}/jurisdiction", tags=["jurisdiction"])


@router.post("/screen")
def screen(matter_id: str):
    res = jurisdiction_engine.screen(get_matter(matter_id))
    return json.loads(canonical_json(res))
