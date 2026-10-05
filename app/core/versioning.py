"""Version stamps recorded in every audit snapshot (decision provenance)."""
import hashlib
from pathlib import Path

ENGINE_VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]


def _hash_files(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def rules_version() -> str:
    """Content hash of rules/*.yaml: changes whenever any rule changes."""
    return _hash_files(list((ROOT / "rules").glob("*.yaml")))[:16]


def taxonomy_version() -> str:
    return _hash_files(list((ROOT / "taxonomy").glob("*.yaml")))[:16]


def corpus_version() -> str:
    """Content hash of verified-provision registry modules."""
    return _hash_files(list((ROOT / "app" / "legal" / "provisions").glob("*.py")))[:16]


def precedent_version() -> str:
    reg = ROOT / "precedents" / "registry.json"
    return _hash_files([reg])[:16] if reg.exists() else "none"


def current_versions() -> dict:
    return {
        "engine": ENGINE_VERSION,
        "rules": rules_version(),
        "taxonomy": taxonomy_version(),
        "legal_corpus": corpus_version(),
        "precedent_corpus": precedent_version(),
    }
