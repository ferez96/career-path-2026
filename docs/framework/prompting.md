# Prompting rules & language — Career Path 2026

Behavioral rules for the AI Assistant: what every report must contain, how to handle missing data, and which language to use for repo content vs chat.

## Language

- **Repository default:** English-first (docs, templates, Cursor skills under `docs/skills/`, `prompts/` redirect stubs, and structured outputs in this repo).
- **Chat with your agent:** You may use Vietnamese (or another language) when talking to the assistant; the assistant should follow your language in conversation while keeping **tracked public-bound artifacts** (`docs/`, `templates/`, `docs/skills/`, `prompts/`, root `README.md` / `CURSOR.md`, etc.) aligned with English-first unless you ask otherwise. **`data/**` is a private local vault** — English-first is still fine for notes, but there is **no** requirement to PII-sanitize content that stays only there.

## Prompting rules (for AI Assistant)

- Follow `docs/SANITIZATION_CHECKLIST.md` when preparing **public-bound** edits (anything that will be committed on `master` outside the private `data/` tree). Outputs that remain **only under `data/`** do not need that checklist.
- Do not invent company/JD facts.
- If data is missing, clarify before concluding.
- Prefer structured tables/checklists.
- Use Obsidian vault navigation to minimize context load: start from `data/Home.md`, `data/atlas/Navigation — JD and Opportunities.md`, `data/opportunities/Central Opportunities.md`, or a single `* Opportunity Index.md`; then read only the linked leaf notes needed for the answer.
- Prefer targeted commands over broad reads when inspecting the vault: `obsidian read vault=data "path=<note path>"`, `obsidian links vault=data "path=<note path>"`, and `python scripts/vault_hub_wikilinks.py` for hub link health.
- Do not load whole folders, raw JD binaries, or long message exports unless the current task explicitly requires source extraction; use normalized `data/jds/*.md` and linked reports first.
- Always include:
  - Main insight
  - Recommended actions
  - Next step within 24h
- Every report must have **Assumptions** and **Risk**.
