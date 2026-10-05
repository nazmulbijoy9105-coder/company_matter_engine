"""Orchestrates stages 2-10 for one matter. OUT_OF_SCOPE stops after the screen (D2):
no further engines run, only a routing note."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from app.audit.provenance import provenance
from app.domain.matter import Matter
from app.domain.states import ScopeOutcome
from app.engines import (argument_engine, evidence_engine, issue_engine, jurisdiction_engine,
                         maintainability_engine, matter_classifier, relief_engine)
from app.evidence.conflict_detection import find_conflicts
from app.legal.rules.rulebook import RuleBook


@dataclass
class PipelineResult:
    scope: object
    classification: Optional[object] = None
    maintainability: Optional[object] = None
    relief: Optional[list] = None
    issues: Optional[list] = None
    evidence_coverage: Optional[dict] = None
    argument_skeletons: Optional[list] = None
    fact_conflicts: Optional[dict] = None
    provenance: Optional[dict] = None

    @property
    def stopped_at_scope(self) -> bool:
        return self.maintainability is None


def run(matter: Matter, book: Optional[RuleBook] = None) -> PipelineResult:
    book = book or RuleBook.load()
    scope = jurisdiction_engine.screen(matter, book)
    if scope.outcome == ScopeOutcome.OUT_OF_SCOPE:
        return PipelineResult(scope=scope)
    classification = matter_classifier.classify(matter)
    maint = maintainability_engine.evaluate(matter, book)
    relief = relief_engine.evaluate(matter, scope, maint, book)
    return PipelineResult(
        scope=scope, classification=classification, maintainability=maint, relief=relief,
        issues=issue_engine.build_issues(scope, maint, relief),
        evidence_coverage=evidence_engine.coverage(matter, book),
        argument_skeletons=argument_engine.skeletons(maint),
        fact_conflicts=find_conflicts(matter.facts),
        provenance=provenance(scope, maint),
    )
