# Career Path 2026

Personal system for **JD analysis and fit scoring**, **opportunity pipeline tracking**, and (locally) **weekly planning and reviews**. The committed tree is framework, templates, config, and small Python helpers; your career state lives under `data/` (gitignored).

## Data safety

Commit code and framework docs normally. Keep personal data (profiles, opportunities, notes) in `data/`; it is gitignored automatically. Do not put PII in committed code.

## Language

Docs, templates, and Assistant skills (`SKILL.md` under `docs/skills/`) in this repo are **English-first**. You can still chat with your agent in another language; see `docs/framework/prompting.md` (Language).

## Repository layout

Full tree: **`docs/REPO_LAYOUT.md`**. Release notes: **`CHANGELOG.md`**. Main areas:

| Area | Role |
|:-----|:-----|
| **`AGENTS.md`** + **`docs/framework/`** | Operating framework: personas, workflows, fit weights, prompting, cadence. |
| **`docs/skills/`** | Canonical Cursor-style skills (JD process, opportunities, company brief, …). |
| **`config/`** | Agent context index (`context_manifest.yaml`) |
| **`data/`** | Data vault root: profile, opportunities, JD notes, weekly files (gitignored). Start from **`data/atlas/Navigation — JD and Opportunities.md`**. |
| **`templates/`** | YAML and Markdown shells (e.g. `master_template.yaml`, opportunity tracker schema, report templates). |
| **`scripts/`** | Vault helpers and **`scripts/opp.py`** for writes to `data/opportunities.yaml` (prefer the CLI over hand-editing YAML). |
| **`packages/wisp/`** | Optional **pre-alpha** local web experiment (job decision support); see **`packages/wisp/README.md`**. Not required for the career framework. |

## Git workflow

Single-branch workflow on `main`. Data stays local via `.gitignore`.

- Code and framework commit normally.
- Personal work stays in `data/` (gitignored).
- No PII in committed code.

Versioning and release notes: **`CHANGELOG.md`**.

## Agent personas (Copilot vs Assistant)

**Copilot** maintains framework, tooling, and Git hygiene. **Assistant** runs JD analysis, fit scoring, planning, and opportunity workflows. See **`docs/AGENT_ROLES.md`** and **`AGENTS.md`**.

## Git usage

Track source documents and planning data in Git while excluding generated artifacts and local secrets via `.gitignore`.

Suggested commit pattern:

- `docs: update career growth framework`
- `data: add weekly progress file` (only if you intentionally commit a non-secret sample; default is local-only)
- `templates: refine capability analysis template`

## License

This project is licensed under the MIT License. See `LICENSE`.

## Operating flow

1. Keep **`data/master.yaml`** as the canonical profile (headline, direction, targets, skills, experience) for Assistant workflows.
2. **Job search pipeline:** maintain **`data/opportunities.yaml`** (copy from `templates/opportunities_tracker_template.yaml`). Use **`python scripts/opp.py --help`** before CLI writes. Skills: `docs/skills/opportunity-*/SKILL.md`; see `docs/framework/workflows.md` (Opportunity Tracking).
3. Create or update weekly files in **`data/weekly/`** as you prefer.
4. Run capability analysis and planning with templates in **`templates/`**.
5. Keep working notes under **`data/reports/`** as needed (layout notes may live in `data/VAULT_LAYOUT.md` or your atlas hubs).
6. Commit framework changes, docs, and tools. Data stays local.
7. See **`AGENTS.md`** for hub-first vault navigation, skills index, and full context-loading order.

For a minimal bootstrap, see **`QUICKSTART.md`**.
