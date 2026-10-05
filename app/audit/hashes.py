from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def _default(o: Any):
    if isinstance(o, Enum):
        return o.value
    if is_dataclass(o):
        return asdict(o)
    raise TypeError(f"not serialisable: {type(o)}")


def canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, no whitespace, enums/dataclasses flattened."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_default)


def sha256_hex(obj: Any) -> str:
    data = obj if isinstance(obj, bytes) else canonical_json(obj).encode("utf-8")
    return hashlib.sha256(data).hexdigest()
