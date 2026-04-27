# Changelog

All notable changes to **Career Path 2026** are recorded here for releases and public merge notes.

**Format:** inspired by [Keep a Changelog](https://keepachangelog.com/). Versioning follows **Semantic Versioning** where it fits this repo (framework + content, not a runtime API): **MAJOR** = breaking governance/layout; **MINOR** = new workflows, templates, or prompts; **PATCH** = fixes and small doc clarifications.

When cutting a release: move items from `[Unreleased]` into a new `## [x.y.z] - YYYY-MM-DD` section, then tag `vx.y.z` on the merge commit to `public` / `master` as per `docs/BRANCH_WORKFLOW.md`.

---

## [Unreleased]

### Added

- **Token monitor MVP runtime:** `apps/web/flask_server.py` (internal UI + `POST /api/llm/chat`), `apps/cli/main.py`, and `scripts/token-monitor.ps1` for tracked operations.
- **Telemetry architecture skeleton:** new `apps/`, `core/`, and `adapters/` packages with extension points for `index`, `tasks`, and `prompts`.
- **SQLite telemetry storage:** `adapters/storage/sqlite/{migrations.py,repository.py}` with `usage_events`, `monthly_rollups`, and `budget_alerts`.
- **OpenAI provider adapter + wrapper:** `adapters/llm/openai_adapter.py` and `core/tasks/llm_wrapper.py` using `OPENAI_API_KEY`.
- **Cost and budget modules:** `core/cost/{pricing.py,costing.py,budget.py}` plus shared domain types in `core/types.py`.
- **Config files:** `config/token_pricing.yaml` and `config/token_budgets.yaml`.

### Changed

- `README.md`: new Token Monitor MVP section (setup, run commands, env-key handling).
- `docs/REPO_LAYOUT.md`, `config/README.md`: documented runtime/code placement and new config files.

### Fixed

### Removed

---

## [0.0.3] — 2026-04-23

### Added

- **Cursor skills:** assistant workflows in `.cursor/skills/*/SKILL.md` (one directory per workflow). [`config/context_manifest.yaml`](config/context_manifest.yaml) indexes those paths; `prompts/*.md` files are short redirects for stable links.
- **Quick start and bootstrap:** [`QUICKSTART.md`](QUICKSTART.md), [`scripts/bootstrap.ps1`](scripts/bootstrap.ps1) / [`scripts/bootstrap.sh`](scripts/bootstrap.sh), and [`templates/master_template.yaml`](templates/master_template.yaml) for first-time local setup (templates are copied only when the target is missing).
- **Reports:** [`reports/briefs/brief-satellite-platform-backend-role-2026-04.md`](reports/briefs/brief-satellite-platform-backend-role-2026-04.md) — sanitized company/role brief (`derived-sanitized`).
- **GitHub AI review:** PR workflow [`.github/workflows/ai-review.yml`](.github/workflows/ai-review.yml) for automated review comments via GitHub Models, plus review policy context in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

### Changed

- [`reports/README.md`](reports/README.md): link to example brief under `briefs/`.
- **AI review gate:** [`.github/workflows/ai-review.yml`](.github/workflows/ai-review.yml) fails CI on blocking findings, with emphasis on sanitization/PII violations for public-bound changes.
- **Sanitization gate (free-tier friendly):** replaced model-dependent PR review with deterministic checks scoped to public-bound files, avoiding token/model limits on large PRs.
- **English-first repo:** translated remaining Vietnamese in `CURSOR.md`, `docs/AGENT_ROLES.md`, `.cursor/rules/*.mdc`, `prompts/company-brief.md`, `templates/jd_analysis_template.md`, and `CHANGELOG.md` (historical entries); added language notes to [`README.md`](README.md) and the language section in [`CURSOR.md`](CURSOR.md) (chat may use Vietnamese; tracked content stays English-first).
- **Docs and layout:** minor alignment in `docs/AGENT_ROLES.md`, [`docs/REPO_LAYOUT.md`](docs/REPO_LAYOUT.md), [`docs/DATA_CLASSIFICATION.md`](docs/DATA_CLASSIFICATION.md), and [`docs/PUBLIC_REPO_POLICY.md`](docs/PUBLIC_REPO_POLICY.md); `templates/opportunities_tracker_template.yaml` comment tidy.

### Fixed

### Removed

- **Placeholder tree markers:** empty `.keep` files under `data/`, `reports/benchmarks/`, and `reports/briefs/` in favor of bootstrap-driven setup (see `QUICKSTART.md`).

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
