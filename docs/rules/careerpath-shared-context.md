
# Same page — Career Path 2026

## Two agent types (read first)

- **Copilot:** Develop the repo, rules, Git/LFS, governance — see `docs/AGENT_ROLES.md` + rule `agent-copilot.mdc` when editing dev files.
- **Assistant:** Career operations (JD/benchmark, planning, reviews) — see `docs/AGENT_ROLES.md` + rule `agent-assistant.mdc` when editing operational files.

If unsure, follow **When the role is unclear** in `docs/AGENT_ROLES.md`.

## Career direction (reference)

- Prefer summaries in `data/private/master.yaml`: `profile.headline`, `career.direction_summary` — **systems-level delivery**, **ownership**, **AI in production / AI-augmented tooling** when analyzing JDs or roadmaps.

## Every session

- Branch: `personal` → sanitize → `public` (`master`). Do not merge `private-sensitive` or `raw-ingest` into `public`.
- Four classes: `public-reusable`, `derived-sanitized`, `raw-ingest`, `private-sensitive` — `docs/DATA_CLASSIFICATION.md`. If unsure → `NEEDS_REVIEW`.
- No PII in public outputs; missing data → `Unknown`, do not invent.
- Classify changes for publish: `ALLOW_PUBLIC` | `REQUIRE_SANITIZATION` | `PRIVATE_ONLY` — with a short reason.

## Quick reference

- `README.md`, `docs/REPO_LAYOUT.md`, `CURSOR.md`, `docs/BRANCH_WORKFLOW.md`, `docs/PUBLIC_REPO_POLICY.md`, `docs/SANITIZATION_CHECKLIST.md`.
- Agent index: `config/context_manifest.yaml`; JD row map: `templates/jd_catalog_template.csv` → local `config/jd_catalog.csv` (gitignored).

## Language

- Repo content is **English-first**. The user may chat with the agent in **Vietnamese**; follow the user’s conversation language while keeping tracked docs and public-bound outputs English-first unless they ask otherwise.
