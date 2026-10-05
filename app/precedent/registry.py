"""Precedent registry (D9). VERIFIED_PRECEDENT needs ALL of: registry entry, verified source,
case number, court, text. Otherwise UNVERIFIED_REFERENCE, which drafting may not cite as authority.
The shipped registry is intentionally EMPTY: nothing is verified until a lawyer ingests it."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "precedents" / "registry.json"

VERIFIED = "VERIFIED_PRECEDENT"
UNVERIFIED = "UNVERIFIED_REFERENCE"


@dataclass
class PrecedentRecord:
    precedent_id: str
    court: Optional[str] = None             # e.g. "High Court Division"
    division: Optional[str] = None          # e.g. "Company Bench"
    case_number: Optional[str] = None
    decision_date: Optional[str] = None
    bench: Optional[str] = None
    provisions: list[str] = field(default_factory=list)   # provision ids / hook ids
    ratio: Optional[str] = None
    treatment: str = "UNKNOWN"              # GOOD_LAW | DISTINGUISHED | OVERRULED | UNKNOWN
    source_ref: Optional[str] = None
    text_sha256: Optional[str] = None       # integrity of OUR copy, not authenticity
    source_verified: bool = False
    case_number_verified: bool = False
    court_verified: bool = False
    text_verified: bool = False
    verified_by: Optional[str] = None
    verified_on: Optional[str] = None

    @property
    def status(self) -> str:
        ok = (self.source_verified and self.case_number_verified and self.court_verified
              and self.text_verified and self.verified_by and self.verified_on
              and self.case_number and self.court and self.text_sha256)
        return VERIFIED if ok else UNVERIFIED


class PrecedentRegistry:
    def __init__(self, records: Optional[list[PrecedentRecord]] = None):
        self._r = {r.precedent_id: r for r in (records or [])}

    @classmethod
    def load(cls, path: Path = REGISTRY_PATH) -> "PrecedentRegistry":
        if not path.exists():
            return cls([])
        return cls([PrecedentRecord(**d) for d in json.loads(path.read_text(encoding="utf-8"))])

    def get(self, pid: str) -> Optional[PrecedentRecord]:
        return self._r.get(pid)

    def all(self) -> list[PrecedentRecord]:
        return list(self._r.values())

    def status_of(self, pid: str) -> str:
        r = self.get(pid)
        return r.status if r else UNVERIFIED

    def citable(self, pid: str) -> bool:
        """Only VERIFIED_PRECEDENT may be presented as authority."""
        return self.status_of(pid) == VERIFIED
