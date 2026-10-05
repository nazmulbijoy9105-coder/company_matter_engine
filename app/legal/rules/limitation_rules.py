"""Limitation rules. Data lives in rules/limitation_rules.yaml."""
from app.legal.rules.loader import rules


def load() -> dict:
    return rules("limitation_rules")


def entries():
    return load()["rules"]
