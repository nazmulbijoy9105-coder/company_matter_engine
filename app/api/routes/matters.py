import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.dependencies import AUDIT, MATTERS, get_matter
from app.domain.matter import Matter

router = APIRouter(prefix="/matters", tags=["matters"])


class IntakeIn(BaseModel):
    intake_kind: str = "ORIGINAL"
    claimed_label: str | None = None
    mode: str = "LAW_ONLY"
    invoked_hooks: list[str] = Field(default_factory=list)
    requested_relief: list[str] = Field(default_factory=list)
    substance_flags: list[str] = Field(default_factory=list)
    proposed_matter_types: list[str] = Field(default_factory=list)


@router.post("")
def create_matter(body: IntakeIn):
    m = Matter(matter_id=str(uuid.uuid4()), **body.model_dump())
    MATTERS[m.matter_id] = m
    AUDIT.append(m.matter_id, "api", "MATTER_CREATED", {"intake_kind": m.intake_kind})
    return {"matter_id": m.matter_id}


@router.get("/{matter_id}")
def read_matter(matter_id: str):
    m = get_matter(matter_id)
    return {"matter_id": m.matter_id, "invoked_hooks": m.invoked_hooks,
            "requested_relief": m.requested_relief, "facts": len(m.facts)}
