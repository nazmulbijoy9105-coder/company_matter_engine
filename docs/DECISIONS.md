# Design Decisions (binding until superseded here)

## D1 — Scope
Original proceedings before the High Court Division Company Bench only.
Appeals from Company Bench orders are an **extension point** (`intake_kind = APPEAL`
is rejected today with `OUT_OF_SCOPE: appeal_not_supported`). Needs its own intake
(impugned order, grounds) before it is enabled.

## D2 — The scope gate is a screen, and it is asymmetric
The user's label ("company matter") is never evidence. Entry requires a **positive
statutory hook**: an invoked Companies Act provision registered in
`rules/scope_gate_rules.yaml` whose remedy matches the relief claimed.
Default for recovery / contract-in-substance disputes is `OUT_OF_SCOPE`.
False positives (running a full analysis on the wrong forum) are the worst failure.

## D3 — Six evaluation states, one propagation table
`SATISFIED, NOT_SATISFIED, UNKNOWN, DISPUTED, NOT_APPLICABLE, REQUIRES_LAWYER_JUDGMENT`.
Evaluative statutory tests (oppression, mismanagement, just-and-equitable, "in substance")
are never auto-resolved: the engine lays out factors and returns `REQUIRES_LAWYER_JUDGMENT`.
Conjunction precedence (strongest first):
`NOT_SATISFIED > DISPUTED > UNKNOWN > REQUIRES_LAWYER_JUDGMENT > SATISFIED`.
`NOT_APPLICABLE` elements are skipped; all-N/A yields `NOT_APPLICABLE`.

## D4 — Verification debt
Every rule, provision and precedent carries `verification_status`. Nothing in this repo
is `VERIFIED` until a named lawyer checks it against the authentic source and records
`verified_by`, `verified_on`, `source_ref`, `source_sha256`. The engine records every
unverified rule it relied on; **release is blocked while any remain**, unless a lawyer
records an override with a reason.

## D5 — Gate release, not analysis
Analysis may proceed past `UNKNOWN`/`DISPUTED` gates with a recorded `override_reason`
(litigation is routinely run on disputed maintainability). Only
`LAWYER_APPROVED -> RELEASED` is a hard stop.

## D6 — AI never creates a verified fact
AI extraction yields `PROPOSED` facts. Only a human reviewer can set `VERIFIED`.
Two `VERIFIED` facts with the same subject+predicate and different objects become `DISPUTED`.

## D7 — Limitation never defaults
Missing accrual or filing date => `UNKNOWN`. No fallback date, no "assume within time".

## D8 — Audit means tamper-evidence, not re-derivation
If an LLM touches extraction or drafting, outputs are not reproducible. We store the
actual outputs and chain-hash the audit log. We do not claim re-running yields the same text.

## D9 — Precedent is optional and strictly gated
`VERIFIED_PRECEDENT` requires registry entry + verified source + case number + court + text.
A SHA-256 of the stored copy proves the copy is unchanged, not that it is authentic;
authenticity is the lawyer's `verified_by` attestation. Drafting may cite only verified precedent.

## D10 — Legal content in this repo is scaffolding
Section numbers and thresholds in `app/legal/provisions/` and `rules/` came from the
project blueprint, not from the statute text. All are `UNVERIFIED_FROM_BLUEPRINT`.
Citations to 2026 judgments in the blueprint are **not** in the registry and must be
ingested and verified through `app/precedent/` before use.
