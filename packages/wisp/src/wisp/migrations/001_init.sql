-- Wisp v1 initial schema.
--
-- Tables and columns are derived from the data-model section of the plan:
-- jobs · evaluations (heuristic + ai + composite, all persisted) ·
-- decision_checklist · timeline_events · decisions (calibration) ·
-- signal_overrides · enrichments.
--
-- Conventions
-- -----------
-- Empty values:    NULL is the canonical "empty" / "not set" / "unknown".
--                  We do NOT store empty strings or zero defaults to mean
--                  the same thing. Callers translate `None`/`""` on input.
-- CHECK constraints: present only on fields whose values DRIVE LOGIC and
--                  whose domain is small + stable. Informational fields
--                  (sources, types, statuses-of-things) have no CHECK; the
--                  app validates on the way in. This keeps the schema
--                  cheap to extend — adding a new evaluator kind or
--                  enrichment source doesn't require a table rebuild.
-- Timestamps:      ISO-8601 UTC strings via strftime('%Y-%m-%dT%H:%M:%fZ','now').
-- Booleans:        0/1 INTEGER per SQLite convention.
-- List/object cols: JSON-encoded TEXT (see *_json columns); SQLite's JSON1
--                  functions are available but v1 reads whole rows.
-- Auto IDs:        Every PK uses INTEGER PRIMARY KEY AUTOINCREMENT (not
--                  the bare rowid alias). AUTOINCREMENT is slightly slower
--                  on writes and adds a sqlite_sequence table, but it
--                  guarantees deleted IDs are NEVER reused — which is
--                  what you want for stable URLs like /jobs/<id>.
-- Idempotence:     All CREATE statements are IF NOT EXISTS so a partial
--                  application is safely re-runnable.

CREATE TABLE IF NOT EXISTS jobs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    company          TEXT    NOT NULL,
    role             TEXT    NOT NULL,
    location         TEXT,                    -- NULL = unknown
    work_type        TEXT,                    -- 'remote'|'hybrid'|'onsite'|NULL; app-validated
    employment_type  TEXT,                    -- 'full-time'|'part-time'|'contract'|...; app-validated
    -- Display string for the UI ("$130-160k"). The numeric form below is
    -- what the M3 heuristic compares against Profile.salary_floor.
    salary_range     TEXT,
    salary_min       INTEGER,                 -- annualized, post-parse; NULL if not parseable
    salary_max       INTEGER,                 -- annualized; NULL if not parseable
    -- ISO 4217 alpha-3. Default USD because most JDs we see are USD; the
    -- JD parser overrides per-job and the heuristic only compares within
    -- a single currency.
    salary_currency  TEXT    NOT NULL DEFAULT 'USD',
    source           TEXT,                    -- 'paste'|'url'|'screenshot'|'pdf'|'email'; app-validated
    source_url       TEXT,
    raw_content      TEXT,                    -- original JD body
    -- status is the one column whose CHECK earns its keep: it drives the
    -- list-view filter, /overview tiles, and the calibration aggregate.
    -- A bad value here would silently corrupt the UX.
    status           TEXT    NOT NULL DEFAULT 'decide'
                     CHECK (status IN ('saved', 'decide', 'applied', 'skipped')),
    created_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);


CREATE TABLE IF NOT EXISTS evaluations (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id               INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    -- Heuristic and AI rows persist alongside the composite so disagreement
    -- is auditable and the user can see "what each one said". `kind` drives
    -- the merge in composite.py — bad values would silently mis-merge.
    kind                 TEXT    NOT NULL
                         CHECK (kind IN ('heuristic', 'ai', 'composite')),
    -- Numeric invariants worth enforcing at the DB so a code bug can't
    -- write 1.7 or -0.2 and corrupt downstream aggregates.
    fit_score            REAL    NOT NULL
                         CHECK (fit_score >= 0.0 AND fit_score <= 1.0),
    confidence           REAL    NOT NULL
                         CHECK (confidence >= 0.0 AND confidence <= 1.0),
    -- Drives signal_label_for / verdict.py; small fixed domain.
    signal               TEXT    NOT NULL
                         CHECK (signal IN ('yes', 'stretch', 'maybe', 'no', 'pending')),
    signal_label         TEXT    NOT NULL,    -- "Worth pursuing", etc.
    -- Hot brief headline. Nullable because heuristic-only paths may not
    -- generate one (verdict.py decides); UI falls back to signal_label.
    brief_recommendation TEXT,
    brief_reasons_json   TEXT    NOT NULL DEFAULT '[]',  -- list[str], 1-2 items
    -- Cold-storage fields below; collapsed in UI by default.
    summary              TEXT,
    strengths_json       TEXT    NOT NULL DEFAULT '[]',
    gaps_json            TEXT    NOT NULL DEFAULT '[]',
    concerns_json        TEXT    NOT NULL DEFAULT '[]',
    cautions_json        TEXT    NOT NULL DEFAULT '[]',
    recommendation       TEXT,
    evidence_json        TEXT    NOT NULL DEFAULT '[]',  -- [{field, snippet}, ...]
    evaluated_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_evaluations_job_id ON evaluations(job_id);
-- Composite index optimizes "latest <kind> for this job" — the hot-brief
-- query on the list view (50 jobs × "give me current composite each").
CREATE INDEX IF NOT EXISTS idx_evaluations_job_kind_time
    ON evaluations(job_id, kind, evaluated_at DESC);


-- One answer per question per job. Editing replaces the row (UPSERT).
-- value is plain TEXT — the UI may switch from yes/maybe/no to a 1-5
-- scale or custom keys; constraining at the DB locks us in needlessly.
CREATE TABLE IF NOT EXISTS decision_checklist (
    job_id     INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    item_key   TEXT    NOT NULL,
    value      TEXT    NOT NULL,
    updated_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (job_id, item_key)
);


-- Append-only event log. source/state are informational; new tags
-- (e.g. 'cron', 'gmail') will land without schema rebuild.
CREATE TABLE IF NOT EXISTS timeline_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id      INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    label       TEXT    NOT NULL,
    detail      TEXT,
    occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    source      TEXT    NOT NULL,             -- 'user'|'heuristic'|'ai'|'inbox'|...; app-validated
    state       TEXT    NOT NULL DEFAULT 'done'  -- 'done'|'current'|'pending'; app-validated
);

CREATE INDEX IF NOT EXISTS idx_timeline_job_id ON timeline_events(job_id);


-- One row per Apply/Skip/Pending click. Powers the calibration table on
-- /overview: "of jobs I called Strong fit, what fraction did the user
-- actually apply?" `action` is constrained because it directly drives the
-- aggregate; new actions need a deliberate decision.
CREATE TABLE IF NOT EXISTS decisions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id               INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    action               TEXT    NOT NULL
                         CHECK (action IN ('apply', 'skip', 'pending', 'reopen')),
    signal_at_time       TEXT    NOT NULL,
    signal_label_at_time TEXT,
    fit_score_at_time    REAL    NOT NULL,
    confidence_at_time   REAL    NOT NULL,
    decided_at           TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_decisions_job_id ON decisions(job_id);


-- One row per "I disagree" override. user_signal is constrained to the
-- documented domain; original_signal mirrors it for the same reason.
CREATE TABLE IF NOT EXISTS signal_overrides (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    original_signal TEXT    NOT NULL
                    CHECK (original_signal IN ('yes', 'stretch', 'maybe', 'no', 'pending')),
    user_signal     TEXT    NOT NULL
                    CHECK (user_signal IN ('yes', 'stretch', 'maybe', 'no', 'pending')),
    reason          TEXT,
    overridden_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_overrides_job_id ON signal_overrides(job_id);


-- On-demand enrichment results (manual notes today; web-search, Glassdoor,
-- Ollama-summarized comments, etc. as v1.1 providers). Each click of
-- "Enrich with..." adds a row; history preserved across re-runs.
--
-- provider_key is intentionally unconstrained: provider authors register
-- their own keys (`manual_company_notes`, `glassdoor`, `ollama_summary`).
-- status and source are app-validated for the same reason.
CREATE TABLE IF NOT EXISTS enrichments (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id       INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    provider_key TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'done',  -- 'pending'|'running'|'done'|'failed'
    result_json  TEXT,                              -- shape per provider; NULL = no result yet
    source       TEXT    NOT NULL,                  -- 'user'|'ai'|'web'|'api'|'local'|...
    created_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_enrichments_job_provider ON enrichments(job_id, provider_key);
