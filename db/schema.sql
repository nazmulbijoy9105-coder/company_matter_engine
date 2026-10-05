-- STUB-LEVEL SCHEMA (PostgreSQL). Not wired in: the API uses in-memory stores until app/core/database.py exists.
-- Design rules: facts/audit are append-only; verification attestations are never nullable-by-default
-- for VERIFIED rows (enforced by CHECK constraints); client data stays out of logs.

create table users (id uuid primary key, org_id uuid not null, email text unique not null,
                    role text not null check (role in ('INTAKE','REVIEWER','LAWYER','ADMIN')));
create table organizations (id uuid primary key, name text not null);

create table matters (id uuid primary key, org_id uuid not null references organizations(id),
    intake_kind text not null default 'ORIGINAL', claimed_label text, mode text not null default 'LAW_ONLY',
    workflow_state text not null default 'INTAKE', created_at timestamptz not null default now());
create table parties (id uuid primary key, matter_id uuid references matters(id), name text not null, role text not null);
create table companies (id uuid primary key, matter_id uuid references matters(id), name text not null,
    registration_no text, company_type text, listed boolean);

create table documents (id uuid primary key, matter_id uuid references matters(id), evidence_type_id text not null,
    title text not null, sha256 text not null, pages int);
create table document_pages (document_id uuid references documents(id), page_no int, text_ref text, primary key (document_id, page_no));
create table facts (id uuid primary key, matter_id uuid references matters(id), predicate text not null, object jsonb not null,
    source_document uuid references documents(id), source_location text, confidence real,
    status text not null check (status in ('PROPOSED','VERIFIED','DISPUTED','REJECTED')) default 'PROPOSED',
    created_by text not null, created_by_kind text not null check (created_by_kind in ('HUMAN','AI')),
    verified_by text,
    check (status <> 'VERIFIED' or (verified_by is not null and created_by_kind is not null)));
create table fact_sources (fact_id uuid references facts(id), document_id uuid references documents(id), page_no int);
create table evidence_items (id uuid primary key, matter_id uuid references matters(id), document_id uuid references documents(id), evidence_type_id text);

create table legal_sources (id text primary key, kind text, source_ref text, source_sha256 text, verified_by text, verified_on date,
    verification_status text not null check (verification_status in ('UNVERIFIED_FROM_BLUEPRINT','PENDING_AUTHORING','VERIFIED')),
    check (verification_status <> 'VERIFIED' or (source_ref is not null and source_sha256 is not null and verified_by is not null and verified_on is not null)));
create table legal_acts (id text primary key references legal_sources(id), title text, year int);
create table legal_sections (id text primary key references legal_sources(id), act_id text references legal_acts(id), section text, text_verified text);
create table legal_rules (id text primary key, hook text, authoring_status text not null, body jsonb not null);
create table legal_exceptions (id text primary key, rule_id text references legal_rules(id), body jsonb);
create table legal_propositions (id text primary key, section_id text references legal_sections(id), body jsonb);

create table matter_classifications (id uuid primary key, matter_id uuid references matters(id), matter_type_id text, is_primary boolean);
create table jurisdiction_findings (id uuid primary key, matter_id uuid references matters(id), outcome text not null, reasons jsonb, snapshot_hash text);
create table maintainability_findings (id uuid primary key, matter_id uuid references matters(id), gate text not null, detail jsonb, snapshot_hash text);
create table legal_evaluations (id uuid primary key, matter_id uuid references matters(id), rule_set_id text, state text not null, detail jsonb);

create table issues (id uuid primary key, matter_id uuid references matters(id), type_id text, state text);
create table arguments (id uuid primary key, issue_id uuid references issues(id), element_id text, application text, response text);
create table counterarguments (id uuid primary key, argument_id uuid references arguments(id), body text);
create table reliefs (id uuid primary key, matter_id uuid references matters(id), remedy_id text, availability text);

create table precedents (id text primary key, court text, division text, case_number text, decision_date date, treatment text,
    source_ref text, text_sha256 text, source_verified boolean default false, case_number_verified boolean default false,
    court_verified boolean default false, text_verified boolean default false, verified_by text, verified_on date);
create table precedent_sources (precedent_id text references precedents(id), source_ref text, sha256 text);
create table precedent_propositions (precedent_id text references precedents(id), provision_id text, ratio text);
create table precedent_verification (precedent_id text references precedents(id), verifier text, verified_on date, note text);

create table drafts (id uuid primary key, matter_id uuid references matters(id), kind text, created_at timestamptz default now());
create table draft_paragraphs (id uuid primary key, draft_id uuid references drafts(id), text text,
    fact_ids uuid[], rule_set_ids text[], evidence_ids uuid[], precedent_ids text[]);
create table reviews (id uuid primary key, item_id text, reviewer text, role text check (role = 'LAWYER'), decision text, note text, ts timestamptz default now());

create table audit_events (seq bigserial primary key, matter_id uuid, actor text, action text, payload jsonb, ts timestamptz, prev_hash text not null, hash text not null);
create table matter_snapshots (id uuid primary key, matter_id uuid references matters(id), versions jsonb, input_hash text, output_hash text,
    snapshot_hash text not null, outputs jsonb not null, actor text, reviewer text, ts timestamptz);
create table engine_versions (version text primary key, source_hash text);
create table corpus_versions (version text primary key, notes text);
