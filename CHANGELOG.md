# Changelog

All notable changes to **Career Path 2026** are recorded here for releases and public merge notes.

**Format:** inspired by [Keep a Changelog](https://keepachangelog.com/). Versioning follows **Semantic Versioning** where it fits this repo (framework + content, not a runtime API): **MAJOR** = breaking governance/layout; **MINOR** = new workflows, templates, or prompts; **PATCH** = fixes and small doc clarifications.

When cutting a release: move items from `[Unreleased]` into a new `## [x.y.z] - YYYY-MM-DD` section, then tag `vx.y.z` on the merge commit to `public` / `master` as per `docs/BRANCH_WORKFLOW.md`.

---

## [Unreleased]

### Added

- **Reports:** [`reports/briefs/brief-satellite-platform-backend-role-2026-04.md`](reports/briefs/brief-satellite-platform-backend-role-2026-04.md) — sanitized company/role brief (`derived-sanitized`)
- **GitHub AI review:** added PR workflow [`.github/workflows/ai-review.yml`](.github/workflows/ai-review.yml) to generate automated review comments via GitHub Models, plus review policy context [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

### Changed

- [`reports/README.md`](reports/README.md): link to example brief under `briefs/`.
- **AI review gate:** updated [`.github/workflows/ai-review.yml`](.github/workflows/ai-review.yml) to fail CI on blocking findings, with emphasis on sanitization/PII violations for public-bound changes.
- **Sanitization gate (free-tier friendly):** replaced model-dependent PR review with deterministic sanitization checks scoped to public-bound files, avoiding token/model limits on large PRs.
- **English-first repo:** Translated remaining Vietnamese in `CURSOR.md`, `docs/AGENT_ROLES.md`, `.cursor/rules/*.mdc`, `prompts/company-brief.md`, `templates/jd_analysis_template.md`, `CHANGELOG.md` (historical entries); added language notes to [`README.md`](README.md) and [`CURSOR.md`](CURSOR.md) §2 (chat may use Vietnamese; tracked content stays English-first).

### Fixed

### Removed

---

## [0.0.2] — 2026-04-18

### Added

- **Opportunity tracking:** schema [`templates/opportunities_tracker_template.yaml`](templates/opportunities_tracker_template.yaml) (experimental; uses `data/private/opportunities.yaml`); prompts `prompts/opportunity-*.md` (from JD, updates, three report types); report templates `templates/opportunity_report_*.md`; rule [`.cursor/rules/opportunity-tracking.mdc`](.cursor/rules/opportunity-tracking.mdc); Opportunity Tracking section in [`CURSOR.md`](CURSOR.md); entries in [`config/context_manifest.yaml`](config/context_manifest.yaml).
- **JD catalog:** [`templates/jd_catalog_template.csv`](templates/jd_catalog_template.csv) — header row only; copy to `config/jd_catalog.csv` locally (gitignored).
- **Weekly planning:** [`prompts/weekly-planning.md`](prompts/weekly-planning.md) (reused for job search / execution).
- **Company brief:** [`prompts/company-brief.md`](prompts/company-brief.md) (prompt template).
- **Fit / resume vs JD:** [`.cursor/rules/career-path-resume.mdc`](.cursor/rules/career-path-resume.mdc) (cross-check `data/private/master.yaml`).

### Changed

- [`CURSOR.md`](CURSOR.md): target metadata, workflows (benchmark, career decision, weekly, daily), expanded fit weights; added Opportunity workflow.
- [`templates/jd_analysis_template.md`](templates/jd_analysis_template.md): fit scoring (systems ownership + AI when the JD includes it).
- [`templates/weekly_plan_template.md`](templates/weekly_plan_template.md): minor edits.
- [`README.md`](README.md), [`docs/AGENT_ROLES.md`](docs/AGENT_ROLES.md), [`docs/DATA_CLASSIFICATION.md`](docs/DATA_CLASSIFICATION.md), [`docs/REPO_LAYOUT.md`](docs/REPO_LAYOUT.md), [`reports/README.md`](reports/README.md), [`config/README.md`](config/README.md): aligned with opportunity tracking and `reports/private/`.
- [`config/context_manifest.yaml`](config/context_manifest.yaml): added context entries (opportunity + related).
- [`.cursor/rules/careerpath-shared-context.mdc`](.cursor/rules/careerpath-shared-context.mdc), [`.cursor/rules/agent-assistant.mdc`](.cursor/rules/agent-assistant.mdc): updated agent guidance.
- [`.gitignore`](.gitignore): ignore `config/jd_catalog.csv`; ignore `data/daily/` and `data/weekly/` so planning notes stay local on `personal` and off public `master` (see [`docs/BRANCH_WORKFLOW.md`](docs/BRANCH_WORKFLOW.md)).
- [`config/README.md`](config/README.md): document template → local JD catalog workflow.
- [`templates/opportunities_tracker_template.yaml`](templates/opportunities_tracker_template.yaml): `jd_source` comment references the JD catalog template + local file.
- [`docs/BRANCH_WORKFLOW.md`](docs/BRANCH_WORKFLOW.md): squash merge to `master`, sync `personal` after publish.

### Fixed

- Per commit history: license/metadata tweaks after project rename.

### Repo / governance

- [`LICENSE`](LICENSE): minor metadata edits.
- **Publish workflow:** Prefer **squash merge** from `personal` to `master` so the public branch does not replay every intermediate commit from `personal`. After publishing, merge `master` back into `personal` to align trees (documented in `docs/BRANCH_WORKFLOW.md`).

---

## [0.0.1] — 2026-04-16

First baseline tagged `v0.0.1`: career-path repo skeleton, governance docs, core templates/prompts, initial `data/` / `config/`. *(Per-file detail can be expanded if a fuller archive is needed.)*
