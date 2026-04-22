# Agent roles — Copilot vs Assistant

The project separates **two agent types** to avoid mixing goals (repo development vs career operations).

## Copilot (framework development)

**Purpose:** Maintain the repo framework, tooling, rules, governance docs, directory layout, Git/LFS, and safe merges to the public branch.

**Read first:**

- `README.md`
- `docs/BRANCH_WORKFLOW.md`
- `docs/DATA_CLASSIFICATION.md`
- `docs/PUBLIC_REPO_POLICY.md`
- `.gitignore`, `.gitattributes`

**Behavior:**

- Changes must declare **decision mode**: `ALLOW_PUBLIC` | `REQUIRE_SANITIZATION` | `PRIVATE_ONLY`.
- Do not track `private-sensitive` / `raw-ingest` on the `public` (`master`) branch.
- New rules/templates: state track/ignore, public/private, and whether sanitize is required before publish.

## Assistant (analysis & operations)

**Purpose:** Use the repo for benchmark/JD analysis, company briefs, career path, milestones, **opportunity pipeline** (per `CURSOR.md`), planning, and reviews (daily / weekly / monthly when templates exist).

**Read first:**

- `CURSOR.md`
- `templates/*`, `.cursor/skills/**`, `prompts/*` (redirect stubs)
- `docs/SANITIZATION_CHECKLIST.md`
- `config/context_manifest.yaml`, `config/jd_catalog.csv`
- `.cursor/rules/career-path-resume.mdc` when scoring fit/gap vs profile
- `.cursor/rules/opportunity-tracking.mdc` when adding/editing opportunities or generating reports from `data/private/opportunities.yaml`

**Behavior:**

- Prefer **derived-sanitized** context; touch `raw-ingest` only when reconciling source material.
- No PII in outputs intended for public; missing data → `Unknown`, do not invent.
- Structured outputs (tables/checklists), with **Assumptions** and **Risk** when `CURSOR.md` requires them.

## Overlap (both)

- Data flow: `personal` → sanitize → `public` (`master`).
- Four classes: `public-reusable`, `derived-sanitized`, `raw-ingest`, `private-sensitive`; if unclear → `NEEDS_REVIEW`.

## When the role is unclear

Default: tasks mainly touching **`.cursor/`, `.github/`, policy docs, Git config** → treat as **Copilot**. Tasks mainly **filling `data/`, `reports/`, or using analysis templates** → treat as **Assistant**.
