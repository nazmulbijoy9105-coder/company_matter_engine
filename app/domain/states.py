"""Evaluation states and the one propagation table (docs/DECISIONS.md D3)."""
from __future__ import annotations
from enum import Enum
from typing import Iterable


class EvalState(str, Enum):
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    UNKNOWN = "UNKNOWN"
    DISPUTED = "DISPUTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REQUIRES_LAWYER_JUDGMENT = "REQUIRES_LAWYER_JUDGMENT"


# Strongest first. A conjunction takes the first state present in this order.
_PRECEDENCE = [
    EvalState.NOT_SATISFIED,
    EvalState.DISPUTED,
    EvalState.UNKNOWN,
    EvalState.REQUIRES_LAWYER_JUDGMENT,
    EvalState.SATISFIED,
]


def combine_all(states: Iterable[EvalState]) -> EvalState:
    """AND-combine. NOT_APPLICABLE elements are skipped; empty/all-N/A => NOT_APPLICABLE."""
    present = {s for s in states if s != EvalState.NOT_APPLICABLE}
    if not present:
        return EvalState.NOT_APPLICABLE
    for s in _PRECEDENCE:
        if s in present:
            return s
    raise ValueError(f"unhandled states: {present}")


class ScopeOutcome(str, Enum):
    IN_SCOPE_CANDIDATE = "IN_SCOPE_CANDIDATE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    UNCERTAIN_LAWYER_REVIEW = "UNCERTAIN_LAWYER_REVIEW"


class Maintainability(str, Enum):
    MAINTAINABLE = "MAINTAINABLE"
    NOT_MAINTAINABLE = "NOT_MAINTAINABLE"
    UNKNOWN = "UNKNOWN"
    DISPUTED = "DISPUTED"
    LAWYER_JUDGMENT_REQUIRED = "LAWYER_JUDGMENT_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


_TO_MAINT = {
    EvalState.SATISFIED: Maintainability.MAINTAINABLE,
    EvalState.NOT_SATISFIED: Maintainability.NOT_MAINTAINABLE,
    EvalState.UNKNOWN: Maintainability.UNKNOWN,
    EvalState.DISPUTED: Maintainability.DISPUTED,
    EvalState.REQUIRES_LAWYER_JUDGMENT: Maintainability.LAWYER_JUDGMENT_REQUIRED,
    EvalState.NOT_APPLICABLE: Maintainability.NOT_APPLICABLE,
}


def to_maintainability(state: EvalState) -> Maintainability:
    return _TO_MAINT[state]


class ReliefAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    CONDITIONALLY_AVAILABLE = "CONDITIONALLY_AVAILABLE"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    NOT_AVAILABLE = "NOT_AVAILABLE"
