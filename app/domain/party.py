from dataclasses import dataclass
from typing import Optional


@dataclass
class Party:
    party_id: str
    name: str
    role: str                      # APPLICANT | RESPONDENT | COMPANY | OTHER
    is_member: Optional[bool] = None
