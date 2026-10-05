# STUB: arguments routes not implemented; use POST /matters/{id}/analysis for the pipeline
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/matters/{matter_id}/arguments", tags=["arguments"])


@router.get("")
def not_implemented(matter_id: str):
    raise HTTPException(501, "arguments endpoint not implemented yet")
