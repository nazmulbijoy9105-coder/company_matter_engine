"""Relief dependencies. Data lives in rules/relief_rules.yaml."""
from app.legal.rules.loader import rules


def load() -> dict:
    return rules("relief_rules")


def entries():
    return load()["remedies"]
