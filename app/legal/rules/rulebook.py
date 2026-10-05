"""RuleBook: one injectable bundle of all rule data. Engines take a RuleBook so tests
can supply fixtures without touching the YAML on disk."""
from __future__ import annotations
import copy
from dataclasses import dataclass

from app.legal.rules.loader import rules


@dataclass
class RuleBook:
    scope: dict
    jurisdiction: dict
    maintainability: dict
    limitation: dict
    relief: dict
    evidence: dict

    @classmethod
    def load(cls) -> "RuleBook":
        return cls(
            scope=copy.deepcopy(rules("scope_gate_rules")),
            jurisdiction=copy.deepcopy(rules("jurisdiction_rules")),
            maintainability=copy.deepcopy(rules("maintainability_rules")),
            limitation=copy.deepcopy(rules("limitation_rules")),
            relief=copy.deepcopy(rules("relief_rules")),
            evidence=copy.deepcopy(rules("evidence_rules")),
        )

    def hooks(self) -> dict:
        return {h["id"]: h for h in self.scope["hooks"]}

    def unverified_sources(self) -> list[str]:
        out = []
        for name in ("scope", "jurisdiction", "maintainability", "limitation", "relief", "evidence"):
            if getattr(self, name).get("verification_status") != "VERIFIED":
                out.append(f"rules/{name}")
        return out
