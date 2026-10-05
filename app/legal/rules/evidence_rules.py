"""Required evidence per hook. Data lives in rules/evidence_rules.yaml."""
from app.legal.rules.loader import rules


def load() -> dict:
    return rules("evidence_rules")


def entries():
    return load()["required_evidence"]
