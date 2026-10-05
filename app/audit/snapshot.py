"""Matter snapshot: stored OUTPUTS plus input/document hashes and version stamps."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional

from app.audit.hashes import sha256_hex
from app.core.versioning import current_versions
from app.domain.matter import Matter


def build_snapshot(matter: Matter, outputs: dict[str, Any], actor: str,
                   reviewer: Optional[str] = None, versions: Optional[dict] = None,
                   ts: Optional[str] = None) -> dict:
    snap = {
        "matter_id": matter.matter_id,
        "versions": versions or current_versions(),
        "input_hash": sha256_hex(matter),
        "document_hashes": {d.doc_id: d.sha256 for d in matter.documents},
        "outputs": outputs,                      # the actual stored results
        "output_hash": sha256_hex(outputs),
        "actor": actor,
        "reviewer": reviewer,
        "timestamp": ts or datetime.now(timezone.utc).isoformat(),
    }
    snap["snapshot_hash"] = sha256_hex({k: v for k, v in snap.items() if k != "snapshot_hash"})
    return snap
