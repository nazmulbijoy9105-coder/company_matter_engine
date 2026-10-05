"""Prints content hashes of rules, taxonomy, provisions and engine source so a release can pin them.
Run: python -m tools.audit_engine_integrity"""
import hashlib
import json
from pathlib import Path

from app.core.versioning import ROOT, current_versions


def engine_source_hash() -> str:
    h = hashlib.sha256()
    for p in sorted((ROOT / "app" / "engines").glob("*.py")) + sorted((ROOT / "app" / "domain").glob("*.py")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


if __name__ == "__main__":
    print(json.dumps({**current_versions(), "engine_source": engine_source_hash()}, indent=2))
