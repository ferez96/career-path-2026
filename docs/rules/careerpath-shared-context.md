
# Same page — Career Path 2026

## Two agent types (read first)

- **Copilot:** Develop the repo, rules, Git/LFS, governance — see `docs/AGENT_ROLES.md` + rule `agent-copilot.mdc` when editing dev files.
- **Assistant:** Career operations (JD/benchmark, planning, reviews) — see `docs/AGENT_ROLES.md` + rule `agent-assistant.mdc` when editing operational files.

If unsure, follow **When the role is unclear** in `docs/AGENT_ROLES.md`.

## Career direction (reference)

- Prefer summaries in `data/master.yaml`: `profile.headline`, `career.direction_summary` — **systems-level delivery**, **ownership**, **AI in production / AI-augmented tooling** when analyzing JDs or roadmaps.

## Every session

- Single branch (`main`). Code and framework commit normally; data stays local (`data/` is gitignored).
- No PII in committed code; missing data → `Unknown`, do not invent.
- Standard git workflow: feature branch → PR → merge to main.

## Quick reference

- `README.md`, `docs/REPO_LAYOUT.md`, `AGENTS.md`.
- Agent index: `config/context_manifest.yaml`; JD row map: `templates/jd_catalog_template.csv` → local `config/jd_catalog.csv` (gitignored).

## Language

- Repo content is **English-first**. The user may chat with the agent in **Vietnamese**; follow the user’s conversation language while keeping tracked docs and public-bound outputs English-first unless they ask otherwise.
