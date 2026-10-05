# STUB: evidence routes not implemented; use POST /matters/{id}/analysis for the pipeline
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/matters/{matter_id}/evidence", tags=["evidence"])


@router.get("")
def not_implemented(matter_id: str):
    raise HTTPException(501, "evidence endpoint not implemented yet")
