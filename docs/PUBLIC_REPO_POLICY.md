# Public Repo Policy

This repository is intended for sharing framework, templates, and anonymized tracking methods for career path and progress workflows.

## Scope

- Allowed: templates, anonymized weekly planning, anonymized progress tracking, anonymized market benchmark notes.
- Not allowed: personal identifiable information (PII), private mentor/manager contacts, confidential internal details, unsanitized raw source assets.

## Branch Model

- Public branch: `public` (`master`)
- Private branch: `personal`
- Allowed one-way flow: `personal` -> sanitize -> `public` (`master`)
- Never merge `private-sensitive` or `raw-ingest` to `public`

## Data Classification

Policy uses the same four mandatory classes as `docs/DATA_CLASSIFICATION.md`. Do not treat “Public” below as a fourth parallel taxonomy; it describes **what may appear on branch `public` (`master`)** after validation.

| Class | Meaning | Allowed on `public` (`master`) |
|---|---|---|
| `public-reusable` | Framework docs, templates, prompts, operating guides | Yes |
| `derived-sanitized` | Weekly tracking, career CSV, reports after redaction | Yes, only after `docs/SANITIZATION_CHECKLIST.md` |
| `raw-ingest` | Raw JD/benchmark text or binaries before normalization | No — keep on `personal` or local ignore |
| `private-sensitive` | Resume, contacts, private notes, identifiable data | No — keep on `personal` or local ignore |

Examples by path (see matrix for full list):

- `public-reusable`: `CURSOR.md`, `templates/*`, `docs/*`, `docs/skills/**`, `prompts/*` (redirect stubs), `README.md`, `config/context_manifest.yaml`
- `derived-sanitized` (when sanitized): `data/weekly/*.md`, `data/career_path_master.csv`, `reports/**/*.md`, `config/jd_catalog.csv`
- `raw-ingest`: `data/raw/*` (unsanitized inputs; single ingest location)
- `private-sensitive`: `data/private/*`, `private-notes/*`, `interview-notes-private/*`

**Internal-only (not for public branch):** Detailed compensation, identifiable company recruiting notes, or NDA interview details are **`private-sensitive`** or require redaction to become `derived-sanitized`. They may exist on `personal` for your workflow; they must not ship to `public` without `REQUIRE_SANITIZATION` and review.

If classification is unclear, use **`NEEDS_REVIEW`** and block merge to `public` until resolved.

Refer to `docs/DATA_CLASSIFICATION.md` for path-level mapping and `NEEDS_REVIEW` handling.

## Redaction Rules

- Replace people names with aliases such as `Recruiter_1`.
- Avoid exact compensation numbers; use coarse bands if needed.
- Remove tracking query parameters from external links.
- Keep only technical learning insights that are non-identifiable.

## Public Safety Checklist

Before each merge to `public` (`master`):

- [ ] No PII in any tracked file.
- [ ] No private links, calendars, or direct contact info.
- [ ] No raw unsanitized benchmark artifacts.
- [ ] Weekly and pipeline files are anonymized.
- [ ] `.gitignore` covers local-only sensitive directories.
- [ ] Classification follows `docs/DATA_CLASSIFICATION.md`.
- [ ] Decision mode is documented (`ALLOW_PUBLIC`, `REQUIRE_SANITIZATION`, `PRIVATE_ONLY`).

## Incident Response

If sensitive data is accidentally committed:

1. Immediately make the repository private.
2. Remove sensitive files from current revisions.
3. Rewrite Git history to purge leaked content.
4. Rotate any exposed credentials or links.
5. Document and update prevention rules.
