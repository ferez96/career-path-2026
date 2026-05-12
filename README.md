# Career Path 2026

Personal system for career path design, skill progression, and weekly execution tracking.

## Data Safety

Commit code and framework docs normally. Keep personal data (profiles, opportunities, notes) in `data/` — it's gitignored automatically. No PII in committed code.

## Language

Docs, templates, and Assistant skills (`SKILL.md` under `docs/skills/`) in this repo are **English-first**. You can still chat with your agent in Vietnamese (or another language); see `docs/framework/prompting.md` (Language).

## Repository layout

Full tree: **`docs/REPO_LAYOUT.md`**. Release notes: **`CHANGELOG.md`**. Main modules:

| Module | Role |
|:-------|:-----|
| **`docs/`** | Full map + framework governance (rules, workflows, cadence). |
| **`AGENTS.md`** + **`docs/framework/`** | Operating framework index; chunked into workflows, fit-weights, prompting, and cadence. |
| **`config/`** | Agent index (`context_manifest.yaml`, `jd_catalog.csv`). |
| **`data/`** | Career state, working notes, profiles, opportunities (all gitignored). |
| **`docs/skills/`**, **`prompts/`**, **`templates/`** | Cursor Skills (canonical workflows); `prompts/` holds redirect stubs; Markdown + YAML templates (incl. JD analysis, weekly/daily, **opportunity tracker schema**). |
| **`data/reports/`** | Derived notes inside the Obsidian vault: `benchmarks/`, `pipeline/`, `roles/`, `companies/`, etc. (see `data/VAULT_LAYOUT.md`, `data/reports/README.md`). |
| **`apps/`**, **`core/`**, **`adapters/`** | MVP runtime for token/cost tracking (`UI -> API wrapper -> provider`) and future extension points (`index`, `tasks`, `prompts`). |

## Git Workflow

Single-branch workflow on `main`. Data stays local via `.gitignore`.

- Code and framework commit normally.
- Personal work stays in `data/` (gitignored).
- No PII in committed code.

See `docs/BRANCH_WORKFLOW.md` for details.

## Agent roles (Copilot vs Assistant)

This repo distinguishes **Copilot** (developing the framework: rules, Git, docs) from **Assistant** (using the system for career analysis, planning, and reviews). See `docs/AGENT_ROLES.md`.

## Git usage

Track source documents and planning data in Git while excluding generated artifacts and local secrets via `.gitignore`.

Suggested commit pattern:

- `docs: update career growth framework`
- `data: add weekly progress file`
- `templates: refine capability analysis template`

## License

This project is licensed under the MIT License. See `LICENSE`.

## Operating Flow

1. Keep **`data/master.yaml`** as the canonical profile (headline, direction, targets, skills, experience) for Assistant workflows.
2. **Optional — job search pipeline:** maintain **`data/opportunities.yaml`** (copy from `templates/opportunities_tracker_template.yaml`). Workflows: `docs/skills/opportunity-*/SKILL.md` — see `docs/framework/workflows.md` (Opportunity Tracking).
3. Create or update weekly files in `data/weekly/`.
4. Run capability analysis and planning with templates in `templates/`.
5. Keep working notes under `data/reports/` as needed (see `data/reports/README.md`).
6. Commit framework changes, docs, and tools. Data stays local.
7. See `AGENTS.md` for complete context and workflow details.

## Token Monitor MVP

This repository now includes a local-first token/cost monitoring path for tracked LLM requests:

- Internal flow: `UI -> POST /api/llm/chat -> OpenAI API -> SQLite telemetry`.
- Pricing source: `config/token_pricing.yaml` (local config, manually maintained).
- Budget source: `config/token_budgets.yaml` (monthly limits + warning ratio).
- Local database: `data/token_usage.db` (gitignored).

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
    "docs/AGENTS.md"
  ]
}
```

Safety limits:

- Allowed roots only: `data/`, `docs/`, `templates/`, `config/`.
- Out-of-repo and path traversal are blocked.
- Non-UTF8/binary files are skipped.
- Context size is capped and may be truncated.

Do not commit secrets (`OPENAI_API_KEY`) or local DB files.
