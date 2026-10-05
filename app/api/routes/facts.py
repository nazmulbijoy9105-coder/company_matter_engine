import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from app.api.dependencies import AUDIT, get_matter
from app.core.errors import VerificationError
from app.domain.fact import Fact

router = APIRouter(prefix="/matters/{matter_id}/facts", tags=["facts"])


class FactIn(BaseModel):
    predicate: str
    object: Any
    source_document: str | None = None
    source_location: str | None = None
    created_by: str
    created_by_kind: str = "HUMAN"      # AI-created facts are always PROPOSED


class VerifyIn(BaseModel):
    reviewer: str
    actor_kind: str


@router.post("")
def add_fact(matter_id: str, body: FactIn):
    m = get_matter(matter_id)
    f = Fact(fact_id=f"FACT-{uuid.uuid4().hex[:8]}", matter_id=matter_id, **body.model_dump())
    m.facts.append(f)
    AUDIT.append(matter_id, body.created_by, "FACT_PROPOSED", {"fact_id": f.fact_id})
    return {"fact_id": f.fact_id, "status": f.status.value}


@router.post("/{fact_id}/verify")
def verify_fact(matter_id: str, fact_id: str, body: VerifyIn):
    m = get_matter(matter_id)
    f = next((x for x in m.facts if x.fact_id == fact_id), None)
    if f is None:
        raise HTTPException(404, "fact not found")
    try:
        f.verify(body.reviewer, body.actor_kind)
    except VerificationError as e:
        raise HTTPException(403, str(e))
    AUDIT.append(matter_id, body.reviewer, "FACT_VERIFIED", {"fact_id": fact_id})
    return {"fact_id": fact_id, "status": f.status.value}
