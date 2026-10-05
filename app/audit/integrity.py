from __future__ import annotations

from app.audit.hashes import sha256_hex


def verify_snapshot(snap: dict) -> list[str]:
    """Returns a list of problems; empty means the snapshot is internally consistent."""
    problems = []
    if sha256_hex(snap["outputs"]) != snap["output_hash"]:
        problems.append("output_hash_mismatch")
    body = {k: v for k, v in snap.items() if k != "snapshot_hash"}
    if sha256_hex(body) != snap["snapshot_hash"]:
        problems.append("snapshot_hash_mismatch")
    return problems
