"""In-memory stores for the MVP. REPLACE with the SQL layer (db/schema.sql) before real use."""
from app.audit.audit_log import AuditLog
from app.domain.matter import Matter

MATTERS: dict[str, Matter] = {}
AUDIT = AuditLog()


def get_matter(matter_id: str) -> Matter:
    from fastapi import HTTPException
    m = MATTERS.get(matter_id)
    if m is None:
        raise HTTPException(404, "matter not found")
    return m
