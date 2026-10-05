# Company Matter Engine — Blueprint (HCD Company Bench, Bangladesh)

Pipeline (state machine, `app/workflow/state_machine.py`):

```
INTAKE -> FACT_COLLECTION -> EVIDENCE_REVIEW -> CLASSIFIED -> JURISDICTION_CHECK
-> MAINTAINABILITY_CHECK -> LEGAL_ANALYSIS -> PRECEDENT_RESEARCH (optional)
-> ISSUE_FORMULATION -> ARGUMENT_ANALYSIS -> RELIEF_ANALYSIS -> DRAFTING
-> LAWYER_REVIEW -> APPROVED -> FROZEN
```

| # | Stage | Module | Status |
|---|-------|--------|--------|
| 1 | Intake | `domain/matter.py`, `api/routes/matters.py` | implemented (in-memory) |
| 2 | Evidence & facts | `evidence/fact_mapping.py`, `evidence/conflict_detection.py` | implemented |
| 3 | Classifier (multi-label) | `engines/matter_classifier.py` | implemented |
| 4 | Scope/jurisdiction screen | `engines/jurisdiction_engine.py` | implemented |
| 5 | Maintainability | `engines/maintainability_engine.py`, `engines/limitation_engine.py` | implemented |
| 6 | Legal corpus | `legal/provisions/*`, `corpus/` | **UNVERIFIED stubs** |
| 7 | Legal evaluation | `engines/statutory_engine.py`, `domain/states.py` | implemented |
| 8 | Precedent (optional) | `precedent/*` | registry + verification implemented; ingestion stub |
| 9 | Issue / argument | `engines/issue_engine.py`, `engines/argument_engine.py` | implemented (structural) |
| 10 | Relief | `engines/relief_engine.py` | implemented |
| 11 | Drafting | `engines/drafting_engine.py`, `drafting/*` | provenance + citation guard implemented; templates stub |
| 12 | Lawyer review | `workflow/review.py`, `workflow/gates.py` | implemented |
| 13 | Audit / freeze | `audit/*`, `workflow/freeze.py` | implemented |

Modes: `LAW_ONLY` (default), `LAW_PLUS_PRECEDENT`, `PRECEDENT_ONLY`.

Hard gates: Scope -> Maintainability -> Legal sufficiency -> Release (only the last is a hard stop; see D5).

Data, not code: `taxonomy/*.yaml` (CM-001..040, REM-*, EV-*), `rules/*.yaml`.
`tools/validate_legal_corpus.py` checks cross-references between them on every CI run.

Honest status of legal content: see `docs/DECISIONS.md` D4 and D10, and run
`python -m tools.status_report`.
