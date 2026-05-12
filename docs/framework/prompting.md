# Prompting rules & language

Behavioral rules for the AI Assistant: what every report must contain, how to handle missing data, and which language to use for repo content vs chat.

## Language

- **Repository default:** English-first (docs, templates, Cursor skills under `docs/skills/`, `prompts/` redirect stubs, and structured outputs in this repo).
- **Chat with your agent:** You may use Vietnamese (or another language) when talking to the assistant; the assistant should follow your language in conversation while keeping **tracked public-bound artifacts** (`docs/`, `templates/`, `docs/skills/`, `prompts/`, root `README.md` / `AGENTS.md`, etc.) aligned with English-first unless you ask otherwise. **`data/**` is a private local vault**.

## Prompting rules (for AI Assistant)

- No PII in committed code. Keep personal data in `data/` (gitignored).
- Do not invent company/JD facts.
- If data is missing, clarify before concluding.
- Prefer structured tables/checklists.
- Use Obsidian vault navigation to minimize context load; then read only the linked leaf notes needed for the answer.
- Prefer targeted commands over broad reads when inspecting files.
- Do not load whole folders, raw JD binaries, or long message exports unless the current task explicitly requires source extraction.
- Always include:
  - Main insight
  - Recommended actions
  - Next step within 24h
- Every report must have **Assumptions** and **Risk**.
