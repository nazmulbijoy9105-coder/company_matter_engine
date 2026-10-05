from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.domain.fact import Fact
from app.domain.evidence import Document

MODES = ("LAW_ONLY", "LAW_PLUS_PRECEDENT", "PRECEDENT_ONLY")


@dataclass
class Matter:
    matter_id: str
    intake_kind: str = "ORIGINAL"                 # ORIGINAL | APPEAL (unsupported, D1)
    claimed_label: Optional[str] = None           # user's own label; NEVER evidence (D2)
    mode: str = "LAW_ONLY"
    invoked_hooks: list[str] = field(default_factory=list)       # e.g. HOOK-CA-233
    requested_relief: list[str] = field(default_factory=list)    # REM-xxx
    substance_flags: list[str] = field(default_factory=list)     # reviewer-set, see scope rules
    proposed_matter_types: list[str] = field(default_factory=list)  # reviewer choice among candidates
    facts: list[Fact] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    parties: list[dict] = field(default_factory=list)
    company: Optional[dict] = None

    def __post_init__(self):
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
