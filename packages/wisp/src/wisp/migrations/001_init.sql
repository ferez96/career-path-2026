-- Wisp v1 initial schema.
--
-- Tables and columns are derived from the data-model section of the plan:
-- jobs · evaluations (heuristic + ai + composite, all persisted) · decision_checklist
-- · timeline_events · decisions (calibration) · signal_overrides · enrichments.
--
-- All timestamps are ISO-8601 UTC strings via `strftime('%Y-%m-%dT%H:%M:%fZ','now')`.
-- Booleans are stored as 0/1 INTEGER per SQLite convention.
-- Multi-value fields (lists of strings) are stored as JSON-encoded TEXT;
-- callers parse with json.loads. SQLite's JSON1 functions are available
-- everywhere we deploy but we don't use them here in v1.
--
-- All ``CREATE`` statements are ``IF NOT EXISTS`` so a partial application
-- (an unlikely failure between executescript and the schema_migrations
-- insert) is safely re-runnable.

CREATE TABLE IF NOT EXISTS jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company         TEXT    NOT NULL,
    role            TEXT    NOT NULL,
    location        TEXT    NOT NULL DEFAULT '',
    work_type       TEXT    NOT NULL DEFAULT '' CHECK (work_type IN ('', 'remote', 'hybrid', 'onsite')),
    employment_type TEXT    NOT NULL DEFAULT '' CHECK (employment_type IN ('', 'full-time', 'part-time', 'contract', 'internship')),
    salary_range    TEXT    NOT NULL DEFAULT '',
    source          TEXT    NOT NULL DEFAULT 'paste' CHECK (source IN ('paste', 'url', 'screenshot', 'pdf', 'email')),
    source_url      TEXT    NOT NULL DEFAULT '',
    raw_content     TEXT    NOT NULL DEFAULT '',
    status          TEXT    NOT NULL DEFAULT 'decide' CHECK (status IN ('saved', 'decide', 'applied', 'skipped')),
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);


CREATE TABLE IF NOT EXISTS evaluations (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id               INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    -- Heuristic and AI rows are persisted alongside the composite so
    -- disagreement is auditable and the user can see "what each one said".
    kind                 TEXT    NOT NULL CHECK (kind IN ('heuristic', 'ai', 'composite')),
    fit_score            REAL    NOT NULL CHECK (fit_score >= 0.0 AND fit_score <= 1.0),
    confidence           REAL    NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    signal               TEXT    NOT NULL CHECK (signal IN ('yes', 'stretch', 'maybe', 'no', 'pending')),
    -- Natural-tone label shown next to the signal: "Worth pursuing", etc.
    signal_label         TEXT    NOT NULL,
    -- Advisory verdict, ≤ ~140 chars; this is the hot brief headline.
    brief_recommendation TEXT    NOT NULL,
    -- 1-2 short bullets ranked for the hot brief (JSON list[str]).
    brief_reasons_json   TEXT    NOT NULL DEFAULT '[]',
    -- Long-form fields below are cold storage; collapsed in UI by default.
    summary              TEXT    NOT NULL DEFAULT '',
    strengths_json       TEXT    NOT NULL DEFAULT '[]',
    gaps_json            TEXT    NOT NULL DEFAULT '[]',
    concerns_json        TEXT    NOT NULL DEFAULT '[]',
    cautions_json        TEXT    NOT NULL DEFAULT '[]',
    recommendation       TEXT    NOT NULL DEFAULT '',
    -- Cited evidence: a list of {field, snippet} pairs the model used.
    evidence_json        TEXT    NOT NULL DEFAULT '[]',
    evaluated_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_evaluations_job_id ON evaluations(job_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_job_kind ON evaluations(job_id, kind);


-- The user's answers to the decision checklist. (job_id, item_key) is the
-- natural composite key — one answer per question per job. Editing
-- replaces the row.
CREATE TABLE IF NOT EXISTS decision_checklist (
    job_id     INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    item_key   TEXT    NOT NULL,
    value      TEXT    NOT NULL CHECK (value IN ('yes', 'maybe', 'no')),
    updated_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (job_id, item_key)
);


-- Append-only event log for a job. Each apply/skip/eval lands one row.
CREATE TABLE IF NOT EXISTS timeline_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id      INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    label       TEXT    NOT NULL,
    detail      TEXT    NOT NULL DEFAULT '',
    occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    source      TEXT    NOT NULL CHECK (source IN ('user', 'heuristic', 'ai', 'inbox')),
    state       TEXT    NOT NULL DEFAULT 'done' CHECK (state IN ('done', 'current', 'pending'))
);

CREATE INDEX IF NOT EXISTS idx_timeline_job_id ON timeline_events(job_id);


-- One row per Apply/Skip click. Powers the calibration table on /overview:
-- "of jobs I called Strong fit, what fraction did the user actually apply?"
CREATE TABLE IF NOT EXISTS decisions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    action              TEXT    NOT NULL CHECK (action IN ('apply', 'skip', 'pending', 'reopen')),
    signal_at_time      TEXT    NOT NULL,
    signal_label_at_time TEXT   NOT NULL DEFAULT '',
    fit_score_at_time   REAL    NOT NULL,
    confidence_at_time  REAL    NOT NULL,
    decided_at          TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_decisions_job_id ON decisions(job_id);


-- One row per "I disagree" override. Logged for the user's reflection
-- and (in v2) for prompt/heuristic tuning. Does not retroactively rewrite
-- evaluations; those stay intact for audit.
CREATE TABLE IF NOT EXISTS signal_overrides (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    original_signal TEXT    NOT NULL,
    user_signal     TEXT    NOT NULL CHECK (user_signal IN ('yes', 'stretch', 'maybe', 'no', 'pending')),
    reason          TEXT    NOT NULL DEFAULT '',
    overridden_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_overrides_job_id ON signal_overrides(job_id);


-- Optional, on-demand enrichment results (manual notes today; web-search,
-- Glassdoor, etc. as v1.1 providers). Each click of "Enrich with..." adds
-- one row; history is preserved across re-runs.
CREATE TABLE IF NOT EXISTS enrichments (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id       INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    provider_key TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'done' CHECK (status IN ('pending', 'running', 'done', 'failed')),
    result_json  TEXT    NOT NULL DEFAULT '{}',
    source       TEXT    NOT NULL CHECK (source IN ('user', 'ai', 'web', 'api')),
    by_user      INTEGER NOT NULL DEFAULT 1 CHECK (by_user IN (0, 1)),
    created_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_enrichments_job_provider ON enrichments(job_id, provider_key);
