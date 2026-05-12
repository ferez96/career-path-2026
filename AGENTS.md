# Agents & Personas

Personal career management system.

## Project Goals

Career Path 2026 is a personal system to:
- JD analysis and fit scoring.
- Opportunity pipeline management.
- (Future) Career path tracking and milestone management.
- (Future) Weekly/daily planning and reviews.

## Persona Selection

There are two personas in the project:
- **Assistant**: JD analysis and fit scoring.
- **Copilot**: Framework/governance docs, tooling, Git config.

## Framework Structure

The operating framework is split into focused files under `docs/framework/` so rules and skills can load only what they need:

| File | Contents | Load when |
|:-----|:---------|:----------|
| [`docs/framework/workflows.md`](docs/framework/workflows.md) | Functional scope (career tracking, benchmark intel, learning, planning), record schemas, workflows | Operations: JD/benchmark, planning, reviews, opportunity pipeline |
| [`docs/framework/fit-weights.md`](docs/framework/fit-weights.md) | Target metadata and weighted fit-scoring rubric | Fit/gap scoring, JD analysis, company briefs |
| [`docs/framework/prompting.md`](docs/framework/prompting.md) | Language convention and prompting rules (Assumptions/Risk, no fabrication, structured output) | Any Assistant report or task generating output |
| [`docs/framework/cadence.md`](docs/framework/cadence.md) | Suggested KPIs (career, learning, execution) and weekly cadence | Planning and review tasks |

## Key Paths

- **Local data vault** — `data/`
- **Committed framework layout** — `docs/`, `templates/`, `config/`, `prompts/`, code, framework docs

## Obsidian Vault & Navigation

The working **Obsidian vault** is rooted at **`data/`**. Before loading large exports or scanning folders, route through hub notes and the golden path in **`data/atlas/Navigation — JD and Opportunities.md`**.

**Protocol:**
- Start from hub notes before opening leaf files
- Prefer normalized `data/jds/<slug>.md` and per-opportunity index notes over bulk reads
- Use `obsidian read` / `obsidian links` with **quoted** `path=` when filenames contain spaces
- Run **`python scripts/vault_hub_wikilinks.py`** if a hub link is broken

**Why:** The vault can be large. Broad reads waste tokens and slow responses. Hub-first navigation is required.

## Scripts

`scripts/opp.py` — single-opportunity CLI for writes to `data/opportunities.yaml`. Do not edit YAML directly.

**Before any list/get/stage/close/note/set run:** from the repo root, run `python scripts/opp.py --help` (and `python scripts/opp.py <command> --help` if needed) so you use the current subcommands and flags.

## Skills Index

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

## Context Loading Pattern

For each task:
1. **Profile** — `data/master.yaml` (fit/gap or planning)
2. **Framework doc** — the relevant `docs/framework/*.md` for the task
3. **SKILL.md** — the matching skill file from the table above
4. **Vault routing** — `data/atlas/Navigation — JD and Opportunities.md` to pick the smallest note set before opening leaves
5. **Data** — task-specific files (e.g. `data/opportunities.yaml`, `data/jds/<slug>.md`)

## Supported File Formats

**Input:**
- Markdown
- Plaintext
- PDF
- PNG (OCR if text is present)
- mhtml (Saved HTML from browser)

**Output:**
- Markdown (reports, plans, reviews, etc.)

## Cross-Cutting References

- Persona responsibilities: [`docs/AGENT_ROLES.md`](docs/AGENT_ROLES.md)
- Git workflow: [`docs/BRANCH_WORKFLOW.md`](docs/BRANCH_WORKFLOW.md)
- Context index: [`config/context_manifest.yaml`](config/context_manifest.yaml)
