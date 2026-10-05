"""Cross-reference validator for taxonomy/, rules/ and legal registries.
Run: python -m tools.validate_legal_corpus   (non-zero exit on any problem)."""
from __future__ import annotations
import sys

from app.legal.corpus import registries as R
from app.legal.rules.loader import clear_cache, rules, taxonomy

ELEMENT_TYPES = {"FACT_EXISTS", "THRESHOLD_GTE", "JUDGMENT"}
AUTHORING = {"PENDING", "DRAFT_UNVERIFIED", "VERIFIED"}


def check_matter_types() -> list[str]:
    ids = [m["id"] for m in taxonomy("matter_types")["matter_types"]]
    p = []
    if len(ids) != len(set(ids)):
        p.append("matter_types: duplicate ids")
    expected = [f"CM-{i:03d}" for i in range(1, len(ids) + 1)]
    if ids != expected:
        p.append("matter_types: ids not contiguous CM-001..")
    hooks = set(R.hook_registry())
    for m in taxonomy("matter_types")["matter_types"]:
        for h in m.get("hooks", []):
            if h not in hooks:
                p.append(f"matter_types:{m['id']}: unknown hook {h}")
    return p


def check_hooks() -> list[str]:
    p, rem = [], R.remedy_registry()
    rule_sets = rules("maintainability_rules")["rule_sets"]
    ids = [h["id"] for h in rules("scope_gate_rules")["hooks"]]
    if len(ids) != len(set(ids)):
        p.append("scope hooks: duplicate ids")
    for h in rules("scope_gate_rules")["hooks"]:
        for r in h["remedies"]:
            if r not in rem:
                p.append(f"hook {h['id']}: unknown remedy {r}")
        if h.get("covered_by") and h["covered_by"] not in rule_sets:
            p.append(f"hook {h['id']}: covered_by {h['covered_by']} not a rule set")
        if "section_status" not in h:
            p.append(f"hook {h['id']}: missing section_status")
    for f, cfg in rules("scope_gate_rules")["substance_flags"].items():
        if cfg.get("routes_to") and cfg["routes_to"] not in rem:
            p.append(f"substance flag {f}: unknown remedy {cfg['routes_to']}")
    return p


def check_maintainability() -> list[str]:
    p = []
    hooks, ev = R.hook_registry(), R.evidence_registry()
    issues = {i["id"] for i in taxonomy("issue_types")["issue_types"]}
    seen = set()
    for rsid, rs in rules("maintainability_rules")["rule_sets"].items():
        if rs["hook"] not in hooks:
            p.append(f"{rsid}: unknown hook {rs['hook']}")
        if rs["authoring_status"] not in AUTHORING:
            p.append(f"{rsid}: bad authoring_status")
        if rs["authoring_status"] == "DRAFT_UNVERIFIED" and not rs["elements"]:
            p.append(f"{rsid}: DRAFT_UNVERIFIED without elements")
        if rs["authoring_status"] == "PENDING" and rs["elements"]:
            p.append(f"{rsid}: PENDING but has elements (set DRAFT_UNVERIFIED)")
        for e in rs["elements"]:
            if e["id"] in seen:
                p.append(f"{e['id']}: duplicate element id")
            seen.add(e["id"])
            if e["type"] not in ELEMENT_TYPES:
                p.append(f"{e['id']}: bad type {e['type']}")
            if e["type"] in ("FACT_EXISTS", "THRESHOLD_GTE") and "predicate" not in e:
                p.append(f"{e['id']}: missing predicate")
            if e["type"] == "FACT_EXISTS" and "expected" not in e:
                p.append(f"{e['id']}: missing expected")
            if e["type"] == "THRESHOLD_GTE" and "value" not in e:
                p.append(f"{e['id']}: missing value")
            if e["type"] == "JUDGMENT" and not e.get("factors"):
                p.append(f"{e['id']}: JUDGMENT needs factors")
            if e.get("issue") and e["issue"] not in issues:
                p.append(f"{e['id']}: unknown issue {e['issue']}")
            for x in e.get("evidence", []):
                if x not in ev:
                    p.append(f"{e['id']}: unknown evidence type {x}")
    return p


def check_limitation() -> list[str]:
    p, hooks = [], R.hook_registry()
    for r in rules("limitation_rules")["rules"]:
        if r["hook"] not in hooks:
            p.append(f"{r['id']}: unknown hook {r['hook']}")
        if r["authoring_status"] not in AUTHORING:
            p.append(f"{r['id']}: bad authoring_status")
        if r["authoring_status"] == "PENDING" and r["period_days"] is not None:
            p.append(f"{r['id']}: PENDING but period_days set")
        if r["authoring_status"] != "PENDING" and not isinstance(r["period_days"], int):
            p.append(f"{r['id']}: authored rule needs integer period_days")
    return p


def check_relief() -> list[str]:
    p, rem = [], R.remedy_registry()
    rule_sets = rules("maintainability_rules")["rule_sets"]
    for rid, cfg in rules("relief_rules")["remedies"].items():
        if rid not in rem:
            p.append(f"relief: unknown remedy {rid}")
        for rs in cfg.get("requires", []):
            if rs not in rule_sets:
                p.append(f"relief {rid}: unknown rule set {rs}")
    return p


def check_evidence() -> list[str]:
    p, hooks, ev = [], R.hook_registry(), R.evidence_registry()
    for h, req in rules("evidence_rules")["required_evidence"].items():
        if h not in hooks:
            p.append(f"evidence rules: unknown hook {h}")
        for x in req:
            if x not in ev:
                p.append(f"evidence rules {h}: unknown evidence type {x}")
    return p


def check_jurisdiction() -> list[str]:
    p, rem = [], R.remedy_registry()
    for rid in rules("jurisdiction_rules")["forum_routes"]:
        if rid not in rem:
            p.append(f"forum_routes: unknown remedy {rid}")
        elif rem[rid].get("company_bench_remedy"):
            p.append(f"forum_routes: {rid} is a Company Bench remedy")
    return p


def check_provisions() -> list[str]:
    p = []
    reg = R.provision_registry()
    for hid, info in R.section_registry().items():
        h = R.hook_registry()[hid]
        if h["section"] and not info["provisions"]:
            p.append(f"hook {hid}: no provision registered for section {h['section']}")
    for pid, prov in reg.items():
        if prov.statute_id not in R.statute_registry():
            p.append(f"{pid}: unknown statute {prov.statute_id}")
    return p


CHECKS = {
    "matter_types": check_matter_types, "hooks": check_hooks, "maintainability": check_maintainability,
    "limitation": check_limitation, "relief": check_relief, "evidence": check_evidence,
    "jurisdiction": check_jurisdiction, "provisions": check_provisions,
}


def run(names: list[str] | None = None) -> list[str]:
    clear_cache()
    R.matter_registry.cache_clear()
    out = []
    for n in names or CHECKS:
        out += [f"[{n}] {x}" for x in CHECKS[n]()]
    return out


def main(names: list[str] | None = None) -> int:
    problems = run(names)
    for x in problems:
        print("PROBLEM:", x)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
