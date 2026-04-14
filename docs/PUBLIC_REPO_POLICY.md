# Public Repo Policy

This repository is intended for sharing framework, templates, and anonymized tracking methods for job search workflows.

## Scope

- Allowed: templates, anonymized weekly planning, anonymized aggregated tracking.
- Not allowed: personal identifiable information (PII), private recruiter/interviewer data, confidential interview details, unsanitized raw JD assets.

## Data Classification

- Public:
  - `CURSOR.md`
  - `templates/*`
  - `data/weekly/*.md` (sanitized)
  - `data/job_pipeline_master.csv` (sanitized aliases only)
- Internal (do not publish publicly):
  - detailed compensation records
  - identifiable company-specific recruiting notes
  - interview process internals under NDA
- Private local only:
  - contacts (email, phone, calendar links)
  - unsanitized PDF/PNG/text raw JD files
  - private interview notes

## Redaction Rules

- Replace real company names with aliases such as `Company_A`.
- Replace people names with aliases such as `Recruiter_1`.
- Avoid exact compensation numbers; use coarse bands if needed.
- Remove tracking query parameters from external links.
- Keep only technical learning insights that are non-identifiable.

## Public Safety Checklist

Before each commit to public branches:

- [ ] No PII in any tracked file.
- [ ] No private links, calendars, or direct contact info.
- [ ] No raw unsanitized JD artifacts.
- [ ] Weekly and pipeline files are anonymized.
- [ ] `.gitignore` covers local-only sensitive directories.

## Incident Response

If sensitive data is accidentally committed:

1. Immediately make the repository private.
2. Remove sensitive files from current revisions.
3. Rewrite Git history to purge leaked content.
4. Rotate any exposed credentials or links.
5. Document and update prevention rules.
