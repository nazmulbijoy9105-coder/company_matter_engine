"""Honest implementation + verification status. Run: python -m tools.status_report"""
from pathlib import Path

from app.core.versioning import ROOT
from app.legal.corpus import registries as R
from app.legal.rules.loader import rules


def stubs() -> list[str]:
    out = []
    for ext in ("*.py", "*.ts", "*.tsx"):
        for p in ROOT.rglob(ext):
            if "node_modules" in p.parts or "__pycache__" in p.parts:
                continue
            head = p.read_text(encoding="utf-8", errors="ignore").splitlines()[:2]
            if any("STUB:" in line for line in head):
                out.append(str(p.relative_to(ROOT)))
    return sorted(out)


def main() -> None:
    s = stubs()
    print(f"STUB files: {len(s)}")
    for x in s:
        print("  ", x)
    pend = [k for k, v in rules("maintainability_rules")["rule_sets"].items() if v["authoring_status"] == "PENDING"]
    draft = [k for k, v in rules("maintainability_rules")["rule_sets"].items() if v["authoring_status"] == "DRAFT_UNVERIFIED"]
    print("rule sets PENDING authoring:", pend)
    print("rule sets DRAFT_UNVERIFIED:", draft)
    lim = [r["id"] for r in rules("limitation_rules")["rules"] if r["authoring_status"] == "PENDING"]
    print("limitation rules PENDING:", lim)
    unv = [pid for pid, p in R.provision_registry().items() if p.verification_status.value != "VERIFIED"]
    print(f"provisions not VERIFIED: {len(unv)} of {len(R.provision_registry())}")


if __name__ == "__main__":
    main()
