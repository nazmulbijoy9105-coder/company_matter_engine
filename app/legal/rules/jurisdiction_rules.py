"""Scope-gate hooks. Data lives in rules/scope_gate_rules.yaml."""
from app.legal.rules.loader import rules


def load() -> dict:
    return rules("scope_gate_rules")


def entries():
    return load()["hooks"]
