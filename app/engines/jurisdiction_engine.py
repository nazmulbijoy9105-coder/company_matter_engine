"""Scope / jurisdiction SCREEN (stage 4). Asymmetric by design (D2):
entry requires a positive statutory hook whose remedy matches the relief claimed.
The user's label is recorded and ignored."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.domain.matter import Matter
from app.domain.states import ScopeOutcome
from app.legal.corpus.registries import remedy_registry
from app.legal.rules.rulebook import RuleBook


@dataclass
class ScopeResult:
    outcome: ScopeOutcome
    reasons: list[str] = field(default_factory=list)
    hooks_matched: list[str] = field(default_factory=list)
    likely_forum: Optional[str] = None
    notes: list[str] = field(default_factory=list)
    label_ignored: bool = True
    unverified_sources: list[str] = field(default_factory=list)


def screen(matter: Matter, book: Optional[RuleBook] = None) -> ScopeResult:
    book = book or RuleBook.load()
    unverified = book.unverified_sources()
    remedies = remedy_registry()
    flags_cfg = book.scope["substance_flags"]
    hooks = book.hooks()

    def result(outcome, reasons, matched=None, forum=None, notes=None):
        return ScopeResult(outcome, reasons, matched or [], forum, notes or [], True, unverified)

    if matter.intake_kind not in book.scope["supported_intake_kinds"]:
        return result(ScopeOutcome.OUT_OF_SCOPE, [f"{matter.intake_kind.lower()}_not_supported"],
                      forum=book.jurisdiction["appeals"]["note"])

    notes = []
    for flag in matter.substance_flags:
        cfg = flags_cfg.get(flag)
        if cfg is None:
            notes.append(f"UNKNOWN_SUBSTANCE_FLAG:{flag}")
        elif cfg.get("note"):
            notes.append(cfg["note"])

    unregistered = [h for h in matter.invoked_hooks if h not in hooks]
    notes += [f"UNREGISTERED_HOOK:{h}" for h in unregistered]
    valid = [hooks[h] for h in matter.invoked_hooks if h in hooks]

    # Hook is "matched" only if a claimed remedy is one the hook can support.
    matched = [h["id"] for h in valid if set(h["remedies"]) & set(matter.requested_relief)]
    conflicting_flags = [f for f in matter.substance_flags if flags_cfg.get(f, {}).get("hook_conflict")]

    if not matched:
        reasons = ["no_positive_statutory_hook"]
        if valid:
            reasons = ["invoked_hook_does_not_support_relief_claimed"]
        forum = _forum(matter, conflicting_flags, flags_cfg, book, remedies)
        return result(ScopeOutcome.OUT_OF_SCOPE, reasons, forum=forum, notes=notes)

    if conflicting_flags:
        return result(ScopeOutcome.UNCERTAIN_LAWYER_REVIEW,
                      [f"substance_may_be_non_company:{f}" for f in conflicting_flags],
                      matched=matched, forum=_forum(matter, conflicting_flags, flags_cfg, book, remedies),
                      notes=notes)

    return result(ScopeOutcome.IN_SCOPE_CANDIDATE, ["positive_statutory_hook_matched"],
                  matched=matched, notes=notes)


def _forum(matter, conflicting_flags, flags_cfg, book, remedies) -> str:
    routes = book.jurisdiction["forum_routes"]
    for f in conflicting_flags:
        rem = flags_cfg[f].get("routes_to")
        if rem in routes:
            return routes[rem]
    for rem in matter.requested_relief:
        if not remedies.get(rem, {}).get("company_bench_remedy", True) and rem in routes:
            return routes[rem]
    return book.jurisdiction["default_forum"]
