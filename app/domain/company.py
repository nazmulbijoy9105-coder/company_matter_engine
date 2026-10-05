from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    name: str
    registration_no: Optional[str] = None
    company_type: Optional[str] = None     # private | public | foreign (as stated by intake reviewer)
    listed: Optional[bool] = None
