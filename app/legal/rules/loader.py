"""Cached YAML loaders for rules/ and taxonomy/. Rules are data; engines read them here."""
from functools import lru_cache
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=None)
def _load(rel: str) -> dict:
    with open(ROOT / rel, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def rules(name: str) -> dict:
    return _load(f"rules/{name}.yaml")


def taxonomy(name: str) -> dict:
    return _load(f"taxonomy/{name}.yaml")


def clear_cache() -> None:
    _load.cache_clear()
