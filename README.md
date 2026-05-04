# Career Path 2026

Personal system for career path design, skill progression, and weekly execution tracking.

## Public Data Disclaimer

This public repository stores only sanitized and anonymized content.
Do not commit personal data, mentor/manager contacts, or confidential company details.

## Language

Docs, templates, and Assistant skills (`SKILL.md` under `docs/skills/`) in this repo are **English-first**. You can still chat with your agent in Vietnamese (or another language); see `docs/framework/prompting.md` (Language).

## Repository layout

Full tree: **`docs/REPO_LAYOUT.md`**. Release notes: **`CHANGELOG.md`**. Main modules:

| Module | Role |
|:-------|:-----|
| **`docs/`** | Full map + governance (branching, classification, sanitization). |
| **`CURSOR.md`** + **`docs/framework/`** | Operating framework index; chunked into workflows, fit-weights, prompting, and cadence. |
| **`config/`** | Agent index (`context_manifest.yaml`, `jd_catalog.csv`). |
| **`data/`** | Tracked state + local raw/private (gitignored paths in layout doc). |
| **`docs/skills/`**, **`prompts/`**, **`templates/`** | Cursor Skills (canonical workflows); `prompts/` holds redirect stubs; Markdown + YAML templates (incl. JD analysis, weekly/daily, **opportunity tracker schema**). |
| **`reports/`** | Sanitized outputs (`benchmarks/`, `briefs/`); full-detail / PII-heavy outputs under `reports/private/` (gitignored). |
| **`apps/`**, **`core/`**, **`adapters/`** | MVP runtime for token/cost tracking (`UI -> API wrapper -> provider`) and future extension points (`index`, `tasks`, `prompts`). |

## Two-Branch Architecture

- `public` (`master`) is the public branch.
- `personal` is the private operating branch.
- Data flow is one-way: `personal` -> sanitize -> `public`.
- Never merge `private-sensitive` or `raw-ingest` into `public`.

Branch and merge rules:

- `docs/BRANCH_WORKFLOW.md`
- `docs/DATA_CLASSIFICATION.md`

## Agent roles (Copilot vs Assistant)

This repo distinguishes **Copilot** (developing the framework: rules, Git, docs) from **Assistant** (using the system for career analysis, planning, and reviews). See `docs/AGENT_ROLES.md`.

## Git usage

Track source documents and planning data in Git while excluding generated artifacts and local secrets via `.gitignore`.

Suggested commit pattern:

- `docs: update career growth framework`
- `data: add weekly progress file`
- `templates: refine capability analysis template`

## Pull request sanitization gate

- Workflow: `.github/workflows/ai-review.yml` runs on PR updates and posts one gate report comment.
- The gate scans **public-bound changed files only** and blocks on risky patterns (PII/secrets/private-only references).
- Designed for free tier and large PRs: deterministic checks only, no model-token usage.
- To enforce merge blocking, set this workflow check as a required status check in branch protection.

## Public Safety Rules

- Follow `docs/PUBLIC_REPO_POLICY.md` before publishing.
- Run `docs/SANITIZATION_CHECKLIST.md` before each public commit.
- Keep raw personal notes and private files in ignored local directories only.
- Public merge gate accepts only `public-reusable` and validated `derived-sanitized`.

## License

This project is licensed under the MIT License. See `LICENSE`.

## Operating flow

1. Keep **`data/private/master.yaml`** as the canonical profile (headline, direction, targets, skills, experience) for Assistant workflows; define or update public milestones in `data/career_path_master.csv`.
2. **Optional — job search pipeline:** maintain **`data/private/opportunities.yaml`** (copy from `templates/opportunities_tracker_template.yaml`); raw JDs live in `data/raw/`. Workflows: `docs/skills/opportunity-*/SKILL.md` — see `docs/framework/workflows.md` (Opportunity Tracking).
3. Create or update the week file in `data/weekly/`.
4. Run capability analysis and planning with templates in `templates/`.
5. Save sanitized outputs to `reports/benchmarks/` and `reports/briefs/` (see `reports/README.md`); opportunity detail reports may go to `reports/private/` until sanitized.
6. Commit meaningful changes.

## Token Monitor MVP

This repository now includes a local-first token/cost monitoring path for tracked LLM requests:

- Internal flow: `UI -> POST /api/llm/chat -> OpenAI API -> SQLite telemetry`.
- Pricing source: `config/token_pricing.yaml` (local config, manually maintained).
- Budget source: `config/token_budgets.yaml` (monthly limits + warning ratio).
- Local database: `data/private/token_usage.db` (gitignored).

### Setup

1. Install Python dependency:
   - `pip install -r apps/requirements-token-monitor.txt`
2. Set provider key in local environment:
   - PowerShell: `$env:OPENAI_API_KEY="your_key_here"`
3. Initialize DB:
   - `scripts/token-monitor.ps1 -Command init-db`

### Run

- Start internal UI + API wrapper:
  - `scripts/token-monitor.ps1 -Command run-web`
- Start with auto-reload for development:
  - `scripts/token-monitor.ps1 -Command run-web-dev`
- Web stack: Flask + HTMX + Bootstrap (`apps/web/flask_server.py`).
- Monthly summary:
  - `scripts/token-monitor.ps1 -Command monthly`
- Monthly alerts:
  - `scripts/token-monitor.ps1 -Command alerts`

### Local file context chat (Cursor-lite)

You can attach local files to improve grounded answers:

- UI: fill **Attached file paths** in the chat form (comma/newline separated).
- JSON API: send `attached_paths` as a list (or comma/newline string).

Example:

```json
{
  "task_type": "weekly-planning",
  "provider": "openai",
  "model": "gpt-4.1-mini",
  "messages": [
    { "role": "user", "content": "Review this week's plan and suggest improvements." }
  ],
  "attached_paths": [
    "data/weekly/2026-W17.md",
    "docs/CURSOR.md"
  ]
}
```

Safety limits:

- Allowed roots only: `data/`, `docs/`, `templates/`, `config/`.
- Out-of-repo and path traversal are blocked.
- Non-UTF8/binary files are skipped.
- Context size is capped and may be truncated.

Do not commit secrets (`OPENAI_API_KEY`) or local DB files.
