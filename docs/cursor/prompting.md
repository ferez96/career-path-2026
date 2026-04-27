# Prompting rules & language — Career Path 2026

Behavioral rules for the AI Assistant: what every report must contain, how to handle missing data, and which language to use for repo content vs chat.

## Language

- **Repository default:** English-first (docs, templates, Cursor skills under `.cursor/skills/`, `prompts/` redirect stubs, and structured outputs in this repo).
- **Chat with your agent:** You may use Vietnamese (or another language) when talking to the assistant; the assistant should follow your language in conversation while keeping **repo artifacts** (files under `docs/`, `templates/`, `.cursor/skills/`, `prompts/`, `reports/` when shared publicly) aligned with English-first unless you ask otherwise.

## Prompting rules (for AI Assistant)

- Follow `docs/SANITIZATION_CHECKLIST.md`.
- Do not invent company/JD facts.
- If data is missing, clarify before concluding.
- Prefer structured tables/checklists.
- Always include:
  - Main insight
  - Recommended actions
  - Next step within 24h
- Every report must have **Assumptions** and **Risk**.
