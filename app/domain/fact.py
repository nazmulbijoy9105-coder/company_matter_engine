"""Facts. AI can only PROPOSE; only a human reviewer can VERIFY (D6)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.core.errors import VerificationError


class FactStatus(str, Enum):
    PROPOSED = "PROPOSED"
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    REJECTED = "REJECTED"


@dataclass
class Fact:
    fact_id: str
    matter_id: str
    predicate: str            # e.g. "applicant.shareholding_percent"
    object: Any               # value
    subject: Optional[str] = None
    date: Optional[str] = None
    source_document: Optional[str] = None   # Document.doc_id
    source_location: Optional[str] = None   # page / clause
    confidence: Optional[float] = None
    status: FactStatus = FactStatus.PROPOSED
    created_by: str = "unknown"
    created_by_kind: str = "HUMAN"          # HUMAN | AI
    verified_by: Optional[str] = None

    def verify(self, reviewer: str, actor_kind: str) -> None:
        if actor_kind != "HUMAN":
            raise VerificationError("only a human reviewer can verify a fact")
        if not reviewer:
            raise VerificationError("reviewer identity required")
        self.status = FactStatus.VERIFIED
        self.verified_by = reviewer

    def dispute(self) -> None:
        self.status = FactStatus.DISPUTED
