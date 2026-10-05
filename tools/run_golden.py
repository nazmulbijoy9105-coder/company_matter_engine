"""Runs tests/golden_cases/*/*.json through the pipeline. Run: python -m tools.run_golden"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from app.core.versioning import ROOT
from app.domain.fact import Fact, FactStatus
from app.domain.matter import Matter
from app.domain.evidence import Document
from app.engines import pipeline
from app.legal.rules.rulebook import RuleBook


def load_case(path: Path) -> tuple[dict, Matter, RuleBook]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    m = spec["matter"]
    facts = [Fact(fact_id=f["id"], matter_id=m["matter_id"], predicate=f["predicate"], object=f["object"],
                  status=FactStatus(f.get("status", "VERIFIED")), created_by="golden") for f in spec.get("facts", [])]
    docs = [Document(**d) for d in spec.get("documents", [])]
    matter = Matter(**{k: v for k, v in m.items()}, facts=facts, documents=docs)
    book = RuleBook.load()
    for patch in spec.get("rulebook_patch", []):
        _apply(book, patch)
    return spec, matter, book


def _apply(book: RuleBook, patch: dict) -> None:
    """patch: {"file": "limitation", "match": {"id": "LIM-CA-233"}, "set": {...}} (TEST FIXTURES ONLY)"""
    target = getattr(book, patch["file"])["rules"]
    for r in target:
        if all(r.get(k) == v for k, v in patch["match"].items()):
            r.update(patch["set"])


def check(spec: dict, res) -> list[str]:
    exp, bad = spec["expect"], []
    if res.scope.outcome.value != exp["scope"]:
        bad.append(f"scope {res.scope.outcome.value} != {exp['scope']}")
    if "maintainability" in exp:
        got = res.maintainability.gate.value if res.maintainability else None
        if got != exp["maintainability"]:
            bad.append(f"maintainability {got} != {exp['maintainability']}")
    for rid, av in exp.get("relief", {}).items():
        got = next((r.availability.value for r in (res.relief or []) if r.remedy_id == rid), None)
        if got != av:
            bad.append(f"relief {rid} {got} != {av}")
    for tid, st in exp.get("issues", {}).items():
        got = next((i.state.value for i in (res.issues or []) if i.type_id == tid), None)
        if got != st:
            bad.append(f"issue {tid} {got} != {st}")
    if "stopped_at_scope" in exp and res.stopped_at_scope != exp["stopped_at_scope"]:
        bad.append(f"stopped_at_scope {res.stopped_at_scope} != {exp['stopped_at_scope']}")
    return bad


def main() -> int:
    fails = 0
    for p in sorted((ROOT / "tests" / "golden_cases").rglob("*.json")):
        spec, matter, book = load_case(p)
        bad = check(spec, pipeline.run(matter, book))
        print(("PASS " if not bad else "FAIL ") + p.relative_to(ROOT).as_posix(), *bad)
        fails += bool(bad)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
