# CareerPath2026 — Claude Code

Personal career management system. Two agent personas; one-way data flow `personal` → sanitize → `master`.

## Role selection

| Files touched | Persona | Spawn with |
|:---|:---|:---|
| `data/`, `reports/`, `templates/`, `.cursor/skills/` | **Assistant** — career operations | `assistant` agent |
| `.cursor/`, `.github/`, `docs/BRANCH_WORKFLOW.md`, policy docs, Git config | **Copilot** — repo framework | `copilot` agent |

When unclear: check `docs/AGENT_ROLES.md`.

## Always apply

- Branch flow: `personal` → sanitize → `master`. Never merge `private-sensitive` or `raw-ingest` into `master`.
- Data classes: `public-reusable` · `derived-sanitized` · `raw-ingest` · `private-sensitive`. Unsure → `NEEDS_REVIEW`.
- No PII in public outputs. Missing data → `Unknown`, never invent.
- Language: repo content English-first; chat may be Vietnamese.

## Framework chunks (load by task)

| Need | File |
|:-----|:-----|
| Workflows, records, opportunity pipeline | `docs/cursor/workflows.md` |
| Fit/gap scoring weights + target profile | `docs/cursor/fit-weights.md` |
| Prompting rules, Assumptions/Risk, language | `docs/cursor/prompting.md` |
| KPIs + weekly cadence | `docs/cursor/cadence.md` |
| Full context index | `config/context_manifest.yaml` |

## Key paths

- Canonical profile: `data/private/master.yaml` (private, gitignored)
- Opportunity tracker: `data/private/opportunities.yaml` (private, gitignored)
- Token usage DB: `data/private/token_usage.db` (private, gitignored)
- Public outputs: `reports/benchmarks/`, `reports/briefs/` (sanitized before commit)
