# CareerPath2026 — Claude

Personal career management system. Two personas; one-way data flow `personal` → sanitize → `master`.

## Persona selection

| Task type | Persona |
|:---|:---|
| JD/benchmark analysis, fit scoring, company briefs, opportunity pipeline, weekly/daily planning, reviews | **Assistant** |
| Editing `.cursor/`, `.github/`, governance docs, branch/Git config, public-merge prep | **Copilot** |

When unclear: check `docs/AGENT_ROLES.md`.

## Always apply

- Branch flow: `personal` → sanitize → `master`. Never merge `private-sensitive` or `raw-ingest` into `master`.
- Data classes: `public-reusable` · `derived-sanitized` · `raw-ingest` · `private-sensitive`. Unsure → `NEEDS_REVIEW`.
- No PII in public outputs. Missing data → `Unknown`, never invent. Every report needs **Assumptions** and **Risk** sections.
- Language: repo content English-first; chat may be Vietnamese.

## Key paths

| Purpose | Path | Class |
|:--|:--|:--|
| Canonical profile | `data/private/master.yaml` | private-sensitive |
| Opportunity tracker | `data/private/opportunities.yaml` | private-sensitive |
| Normalized JDs | `data/jds/<slug>.md` | derived-sanitized |
| JD catalog | `config/jd_catalog.csv` | public-reusable |
| Private reports | `reports/private/` | private-sensitive |
| Public briefs | `reports/briefs/` | derived-sanitized |
| Raw JDs / email | `data/raw/` | raw-ingest |

## Scripts

`scripts/opp.py` — single-opportunity CLI. Use this for all writes to existing opportunities instead of editing the YAML directly.

**Full reference:** `docs/opp-cli.md`

## Framework docs (load by task)

Framework docs live under `docs/framework/`. Skill definitions live under `docs/skills/`. Rule content lives under `docs/rules/`. All are tool-agnostic — Cursor and Claude adapters in `.cursor/` and `.claude/` are thin wrappers only.

| Need | File |
|:-----|:-----|
| Workflows, records, opportunity pipeline | `docs/framework/workflows.md` |
| Fit/gap scoring weights + target profile | `docs/framework/fit-weights.md` |
| Prompting rules, Assumptions/Risk, no-fabrication | `docs/framework/prompting.md` |
| KPIs + weekly operating cadence | `docs/framework/cadence.md` |
| Full context index with token budgets | `config/context_manifest.yaml` |
| Skill definitions (all agents) | `docs/skills/<name>/SKILL.md` |
| Rule content (all agents) | `docs/rules/<name>.md` |

## Skills index

Skills live in `docs/skills/<name>/SKILL.md`. Read the SKILL.md before starting any skill workflow.

| Skill | Trigger phrase | SKILL.md path |
|:------|:--------------|:--------------|
| `jd-process` | "jd-process for X", "process this JD", "full JD workflow" | `docs/skills/jd-process/SKILL.md` |
| `company-brief` | "company brief for X", "research X", "employer due diligence" | `docs/skills/company-brief/SKILL.md` |
| `opportunity-from-jd` | "add opportunity from JD", "import JD to tracker" | `docs/skills/opportunity-from-jd/SKILL.md` |
| `opportunity-update` | "update opportunity", "move X to [stage]", "close opportunity" | `docs/skills/opportunity-update/SKILL.md` |
| `opportunity-report-tracking` | "pipeline report", "tracking list", "pipeline snapshot" | `docs/skills/opportunity-report-tracking/SKILL.md` |
| `opportunity-report-next-steps-one` | "next steps for [company]", "what should I do for X" | `docs/skills/opportunity-report-next-steps-one/SKILL.md` |
| `opportunity-report-next-steps-rollup` | "next steps rollup", "combined backlog", "what's due across all" | `docs/skills/opportunity-report-next-steps-rollup/SKILL.md` |
| `weekly-planning` | "weekly plan", "plan this week", "ISO week plan" | `docs/skills/weekly-planning/SKILL.md` |

## Context loading pattern

For each task, load in this order:
1. **Profile** — `data/private/master.yaml` (fit/gap or planning tasks)
2. **Framework doc** — the relevant `docs/framework/*.md` file for the task type
3. **SKILL.md** — the matching skill file from the table above
4. **Data** — task-specific files per the skill (e.g. `data/private/opportunities.yaml`, `data/raw/`, `data/jds/<slug>.md`, `config/jd_catalog.csv`).