"""Verification helpers. Hash checks prove our stored copy is unchanged (integrity);
authenticity is the lawyer's attestation recorded in verified_by / verified_on."""
from __future__ import annotations

from app.evidence.hash import sha256_bytes
from app.precedent.registry import PrecedentRecord


def text_matches_record(record: PrecedentRecord, text: bytes) -> bool:
    return bool(record.text_sha256) and sha256_bytes(text) == record.text_sha256


def verification_gaps(record: PrecedentRecord) -> list[str]:
    gaps = []
    for flag in ("source_verified", "case_number_verified", "court_verified", "text_verified"):
        if not getattr(record, flag):
            gaps.append(flag)
    for f in ("case_number", "court", "text_sha256", "verified_by", "verified_on"):
        if not getattr(record, f):
            gaps.append(f"missing:{f}")
    return gaps
