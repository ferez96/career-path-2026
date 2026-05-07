# Data Classification Matrix

## Required Classes

- `public-reusable`: templates, docs, reusable sanitized examples.
- `private-sensitive`: real resume, private notes, contacts, identifying data.
- `raw-ingest`: raw JD/benchmark input before normalization/sanitization.
- `derived-sanitized`: generated analysis/planning outputs sanitized for sharing.

If uncertain, classify as `NEEDS_REVIEW` with a short reason.

## Path-Based Defaults

| Path pattern | Class | Track/Ignore | Public publish rule |
|---|---|---|---|
| `docs/*` | `public-reusable` | Track | Allowed |
| `templates/*` | `public-reusable` | Track | Allowed |
| `templates/opportunities_tracker_template.yaml` | `public-reusable` | Track | Allowed (schema only; no real opportunities) |
| `templates/opportunity_report_*.md` | `public-reusable` | Track | Allowed (empty placeholders) |
| `docs/skills/**` | `public-reusable` | Track | Allowed (canonical Assistant `SKILL.md` workflows) |
| `prompts/*` | `public-reusable` | Track | Allowed (redirect stubs to `docs/skills/*/SKILL.md`) |
| `prompts/opportunity-*.md` | `public-reusable` | Track | Allowed |
| `README.md` | `public-reusable` | Track | Allowed |
| `docs/AGENT_ROLES.md` | `public-reusable` | Track | Allowed |
| `CURSOR.md` | `public-reusable` | Track | Allowed |
| `config/README.md` | `public-reusable` | Track | Allowed |
| `config/context_manifest.yaml` | `public-reusable` | Track | Allowed |
| `config/jd_catalog.csv` | `derived-sanitized` | Track | Allowed after checklist (if committed; often gitignored locally) |
| `data/raw/**` | `raw-ingest` | Ignore | Blocked from `master` — unprocessed inputs |
| `data/**` (all other: `private/`, `jds/`, `reports/`, `weekly/`, `atlas/`, `opportunities/`, `*.csv` at vault root, etc.) | `private-sensitive` | Ignore | **Local vault only** (typically gitignored). Not published to `master`; **no in-vault PII sanitization required** for personal use. Run `docs/SANITIZATION_CHECKLIST.md` only when **copying excerpts** into tracked public paths (`docs/`, `templates/`, `README.md`, …). |
| `private-notes/*` | `private-sensitive` | Ignore | Blocked |
| `interview-notes-private/*` | `private-sensitive` | Ignore | Blocked |

## Classification Rules for New Files

For any new file/folder proposal, always document:

1. `Track` or `Ignore`.
2. `Public` or `Private`.
3. Whether `sanitize before publish` is required.

If any of these is unknown, mark file as `NEEDS_REVIEW`.

## Decision Mode Mapping

- `ALLOW_PUBLIC`:
  - class is `public-reusable` or validated `derived-sanitized`
  - no PII
  - sanitization checklist passed
- `REQUIRE_SANITIZATION`:
  - content can become public after redaction/generalization
- `PRIVATE_ONLY`:
  - class is `private-sensitive` or `raw-ingest`
  - or contains unremovable sensitive details
