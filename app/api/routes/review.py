# STUB: review routes not implemented; use POST /matters/{id}/analysis for the pipeline
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/matters/{matter_id}/review", tags=["review"])


@router.get("")
def not_implemented(matter_id: str):
    raise HTTPException(501, "review endpoint not implemented yet")
