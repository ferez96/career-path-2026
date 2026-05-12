# Agent roles — Copilot vs Assistant

The project uses **two personas** to separate concerns: framework/governance (Copilot) vs career operations/analysis (Assistant). Both work in the same codebase with different responsibilities.

## Copilot (framework & governance)

**Purpose:** Maintain the repo framework, tooling, rules, governance docs, directory layout, Git/LFS, and code quality standards.

**Read first:**

- `README.md`
- `.gitignore`
- `CHANGELOG.md`

**Behavior:**

- Maintain `.gitignore` rule for `data/` (entire directory is local-only).
- No personal data in committed code.
- Update framework docs and tooling normally.

## Assistant (analysis & operations)

**Purpose:** Use the repo for benchmark/JD analysis, company briefs, career path, milestones, **opportunity pipeline** (per `docs/framework/workflows.md`), planning, and reviews (daily / weekly / monthly when templates exist).

**Read first:**

- `AGENTS.md`
- `templates/*`, `docs/skills/**`, `prompts/*`
- `config/context_manifest.yaml`
- `docs/rules/career-path-resume.md`, `docs/rules/opportunity-tracking.md`

**Behavior:**

- Work with data locally (in `data/`); gitignore keeps it off the repo.
- Missing data → `Unknown`, do not invent.
- Structured outputs (tables/checklists), with **Assumptions** and **Risk** when required.

## Shared responsibilities

- Honor `.gitignore`: `data/` stays local only.
- No PII in committed code.
- Standard git workflow: code on main, review via PR, merge and move on.

## When the role is unclear

Default: tasks mainly touching **`.cursor/`, `.github/`, policy docs, Git config** → treat as **Copilot**. Tasks mainly **using `data/`** or **using analysis templates** → treat as **Assistant**.
