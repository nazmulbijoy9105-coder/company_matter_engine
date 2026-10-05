"""Corpus records. VERIFIED is unreachable without a named attestation (D4)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.core.errors import VerificationError


class VerificationStatus(str, Enum):
    UNVERIFIED_FROM_BLUEPRINT = "UNVERIFIED_FROM_BLUEPRINT"
    PENDING_AUTHORING = "PENDING_AUTHORING"
    VERIFIED = "VERIFIED"


def _require_attestation(obj) -> None:
    if obj.verification_status == VerificationStatus.VERIFIED:
        missing = [f for f in ("verified_by", "verified_on", "source_ref", "source_sha256")
                   if not getattr(obj, f)]
        if missing:
            raise VerificationError(f"{obj.id}: VERIFIED requires {missing}")


@dataclass(frozen=True)
class Statute:
    id: str
    title: str
    year: int
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED_FROM_BLUEPRINT
    source_ref: Optional[str] = None
    source_sha256: Optional[str] = None
    verified_by: Optional[str] = None
    verified_on: Optional[str] = None

    def __post_init__(self):
        _require_attestation(self)


@dataclass(frozen=True)
class Provision:
    id: str
    statute_id: str
    section: str
    blueprint_topic: Optional[str] = None   # topic as stated in the blueprint, NOT statutory heading
    text: Optional[str] = None              # authentic text, only after lawyer verification
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED_FROM_BLUEPRINT
    source_ref: Optional[str] = None
    source_sha256: Optional[str] = None
    verified_by: Optional[str] = None
    verified_on: Optional[str] = None

    def __post_init__(self):
        _require_attestation(self)
        if self.verification_status != VerificationStatus.VERIFIED and self.text:
            raise VerificationError(f"{self.id}: text may only be stored once VERIFIED")
