"""Argument structure: Issue -> Rule -> Element -> Fact -> Evidence -> Application ->
Counterargument -> Response -> Conclusion. The engine builds the skeleton; a lawyer writes
the reasoning. The engine does not generate persuasive prose."""
from __future__ import annotations
from dataclasses import dataclass, field

from app.core.errors import EngineError

PLACEHOLDER = "[LAWYER TO COMPLETE]"


@dataclass
class ArgumentNode:
    issue_id: str
    rule_set_id: str
    element_id: str
    fact_ids: list[str] = field(default_factory=list)
    evidence_types: list[str] = field(default_factory=list)
    application: str = PLACEHOLDER
    counterargument: str = PLACEHOLDER
    response: str = PLACEHOLDER
    conclusion_state: str = "UNKNOWN"

    def is_complete(self) -> bool:
        return all(v and v != PLACEHOLDER for v in (self.application, self.counterargument, self.response))

    def require_complete(self) -> None:
        if not self.is_complete():
            raise EngineError(f"argument {self.issue_id}/{self.element_id} lacks application, counterargument or response")
