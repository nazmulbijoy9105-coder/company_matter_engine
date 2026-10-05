from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Document:
    doc_id: str
    evidence_type_id: str            # EV-CORP-xxx / EV-GEN-xxx
    title: str
    sha256: Optional[str] = None     # hash of the stored copy (integrity, not authenticity)
    pages: Optional[int] = None
