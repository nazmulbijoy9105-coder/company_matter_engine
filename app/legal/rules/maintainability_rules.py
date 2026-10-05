"""Maintainability rule sets. Data lives in rules/maintainability_rules.yaml."""
from app.legal.rules.loader import rules


def load() -> dict:
    return rules("maintainability_rules")


def entries():
    return load()["rule_sets"]
