"""Canonical registries derived from taxonomy/ and rules/ (data, not branching code).

matter_registry   CM-xxx -> matter type
remedy_registry   REM-xxx -> remedy
evidence_registry EV-xxx  -> evidence type
section_registry  hook -> provisions -> matter types -> rule set -> required evidence -> remedies
"""
from __future__ import annotations
from functools import lru_cache
import importlib

from app.core.errors import UnknownReference
from app.legal.rules.loader import rules, taxonomy

_STATUTE_MODULES = [
    "companies_act_1994", "cpc_1908", "evidence_act_1872", "limitation_act_1908",
    "contract_act_1872", "specific_relief_act_1877", "succession_act_1925",
    "transfer_property_act_1882", "arbitration_act_2001",
]


@lru_cache(maxsize=None)
def matter_registry() -> dict:
    return {m["id"]: m for m in taxonomy("matter_types")["matter_types"]}


@lru_cache(maxsize=None)
def remedy_registry() -> dict:
    return {r["id"]: r for r in taxonomy("remedy_types")["remedies"]}


@lru_cache(maxsize=None)
def evidence_registry() -> dict:
    return {e["id"]: e for e in taxonomy("evidence_types")["evidence_types"]}


@lru_cache(maxsize=None)
def hook_registry() -> dict:
    return {h["id"]: h for h in rules("scope_gate_rules")["hooks"]}


@lru_cache(maxsize=None)
def provision_registry() -> dict:
    out = {}
    for mod in _STATUTE_MODULES:
        m = importlib.import_module(f"app.legal.provisions.{mod}_provisions")
        for p in m.PROVISIONS:
            out[p.id] = p
    return out


@lru_cache(maxsize=None)
def statute_registry() -> dict:
    out = {}
    for mod in _STATUTE_MODULES:
        m = importlib.import_module(f"app.legal.statutes.{mod}")
        out[m.STATUTE.id] = m.STATUTE
    return out


def section_registry() -> dict:
    """hook_id -> {provisions, matter_types, rule_sets, required_evidence, remedies}."""
    rule_sets = rules("maintainability_rules")["rule_sets"]
    req_ev = rules("evidence_rules")["required_evidence"]
    out = {}
    for hid, hook in hook_registry().items():
        out[hid] = {
            "act": hook["act"],
            "section": hook["section"],
            "provisions": [pid for pid, p in provision_registry().items()
                           if p.statute_id == hook["act"] and hook["section"]
                           and p.section in str(hook["section"]).replace("-", ",").split(",")],
            "matter_types": [mid for mid, m in matter_registry().items() if hid in m.get("hooks", [])],
            "rule_sets": [rsid for rsid, rs in rule_sets.items() if rs["hook"] == hid],
            "required_evidence": req_ev.get(hid, []),
            "remedies": hook["remedies"],
        }
    return out


def require_hook(hook_id: str) -> dict:
    try:
        return hook_registry()[hook_id]
    except KeyError:
        raise UnknownReference(f"unregistered hook: {hook_id}")
