from dataclasses import dataclass
from typing import Optional


@dataclass
class Proceeding:
    proceeding_id: str
    forum: str                              # e.g. "HCD Company Bench"
    case_number: Optional[str] = None
    status: Optional[str] = None
    related_to_matter: Optional[str] = None
