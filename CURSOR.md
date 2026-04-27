# Project: Career Path 2026

## Project goals

Career Path 2026 is a personal system to:
- Design long-term career stages (6–12–24 months), **prioritizing systems-level ownership, plus AI/ML in production and AI-augmented tooling to improve delivery** (details in `data/private/master.yaml` → `career.direction_summary`, `profile.headline`).
- Track capability progress and execution outcomes weekly/monthly.
- Plan and review on a weekly/daily cadence.
- Collect and normalize benchmarks from roles/JDs as reference data (applying immediately is optional).
- Produce capability gap reports to guide learning and growth.
- Combine skill sharpening (DSA, System Design, Coding, Problem Solving) with career planning.

## Framework chunks

The operating framework is split into focused files under `docs/cursor/` so rules and skills can load only what they need:

| File | Contents | Load when |
|:-----|:---------|:----------|
| [`docs/cursor/workflows.md`](docs/cursor/workflows.md) | Functional scope (career tracking, benchmark intel, learning, planning), record schemas, and Workflows 1–4 + Opportunity Tracking | Operations: JD/benchmark, planning, reviews, opportunity pipeline |
| [`docs/cursor/fit-weights.md`](docs/cursor/fit-weights.md) | Target metadata (`target_profile`) and weighted fit-scoring rubric | Fit/gap scoring, JD analysis, company briefs |
| [`docs/cursor/prompting.md`](docs/cursor/prompting.md) | Language convention and the Assistant's prompting rules (Assumptions/Risk, no fabrication, structured output) | Any Assistant report or task generating output |
| [`docs/cursor/cadence.md`](docs/cursor/cadence.md) | Suggested KPIs (career, learning, execution) and weekly cadence | Planning and review tasks |

## Supported file formats

**Input:**
- Markdown
- Plaintext
- PDF
- PNG (OCR if text is present)

**Output:**
- Markdown (reports, plans, reviews)
- Plaintext (quick notes)
- CSV/Markdown tables (tracking)
- PDF (optional, final export)

## Cross-cutting references

- Roles (Copilot vs Assistant): [`docs/AGENT_ROLES.md`](docs/AGENT_ROLES.md)
- Branch & merge rules: [`docs/BRANCH_WORKFLOW.md`](docs/BRANCH_WORKFLOW.md)
- Public safety: [`docs/PUBLIC_REPO_POLICY.md`](docs/PUBLIC_REPO_POLICY.md), [`docs/SANITIZATION_CHECKLIST.md`](docs/SANITIZATION_CHECKLIST.md)
- Context index: [`config/context_manifest.yaml`](config/context_manifest.yaml)
