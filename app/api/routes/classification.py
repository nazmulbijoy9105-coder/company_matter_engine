# STUB: classification routes not implemented; use POST /matters/{id}/analysis for the pipeline
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/matters/{matter_id}/classification", tags=["classification"])


@router.get("")
def not_implemented(matter_id: str):
    raise HTTPException(501, "classification endpoint not implemented yet")
