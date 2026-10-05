# Company Matter Engine: HCD Company Bench (Bangladesh)

Deterministic, lawyer-reviewable, fully auditable analysis of original Company Bench matters.
Read `docs/DECISIONS.md` first: it fixes the design choices this code enforces.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q                               # unit + golden tests
python -m tools.validate_legal_corpus   # cross-reference integrity of taxonomy/rules/registries
python -m tools.run_golden              # golden cases through the pipeline
python -m tools.status_report           # what is STUB / PENDING / unverified
uvicorn app.main:app --reload           # API (in-memory stores)
```

## What is real vs scaffolding

- **Real and tested:** state table, scope screen, classifier, rule-set evaluator, limitation logic,
  maintainability, relief, issues, argument skeletons, fact/verification rules, precedent guard,
  drafting guard, review ledger, release gate, audit hash-chain, snapshots, corpus validator.
- **Scaffolding (marked `STUB:` on line 1):** most API routes (501), SQL layer, auth, ingestion,
  extraction, citation parser, drafting templates, frontend.
- **Legal content is NOT verified.** Every section number, threshold and element tree came from the
  project blueprint, not statute text. Nothing is `VERIFIED`; limitation periods and most rule sets
  are `PENDING`; the precedent registry is empty. `release_and_freeze` refuses to release while
  unverified sources remain, unless a lawyer records a waiver with a reason.

## First lawyer tasks (the real critical path)

1. Verify the 9 Companies Act section mappings in `rules/scope_gate_rules.yaml` against the authentic
   text; attach `source_ref` / `source_sha256` / `verified_by` / `verified_on` in `app/legal/provisions/`.
2. Verify the s.233 / s.43 element trees and the threshold in `rules/maintainability_rules.yaml`
   (`value_status: UNVERIFIED`).
3. Author limitation periods in `rules/limitation_rules.yaml` from the Limitation Act text.
4. Author the PENDING rule sets (capital reduction, AGM, reconstruction, winding-up).
5. Ingest and verify precedents one by one; the 2026 judgments cited in the blueprint are NOT in the registry.
# company_matter_engine
