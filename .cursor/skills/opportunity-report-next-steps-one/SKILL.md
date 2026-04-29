---
name: opportunity-report-next-steps-one
description: >-
  Produces next-steps markdown for a single opportunity from opportunities.yaml
  using opportunity_report_next_steps_one template. Use when the user asks for
  one-opportunity next actions, 24–72h moves, or snapshot for a given id.
---

# Report — next steps for one opportunity

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- `data/private/opportunities.yaml` (private)
- Output skeleton: `templates/opportunity_report_next_steps_one.md`

**Task:**
1. Select the record by **`id`**: `<OPPORTUNITY_ID>` (or company + role if user specifies — resolve ambiguity).
2. Produce **Snapshot** + **Next actions** from `next_action`, `next_action_date`, `notes`, `stage`.
3. Populate **Contacts** table from `contacts[]`; if empty, write "None recorded."
4. Populate **Check here (manual)** table from `links`; if empty, write "None recorded."
5. Add **Blockers / risks** from notes and stage.
6. Add **Suggested 24–72h moves** aligned with the workflow style in `docs/cursor/workflows.md` (Workflow 2).
7. **Assumptions** / **Risk**.

**Output:** Markdown for `reports/private/opportunity-next-steps-<id>-<YYYY-MM-DD>.md` or paste-only.

**Constraints:**
- Full detail stays private; sanitize before any public `reports/briefs/` excerpt.
- **Do not fabricate.** Every sentence in the report must be traceable to a field in the YAML record (`stage`, `next_action`, `notes`, `history`, `contacts`, `links`). Do not add general career advice, invented timelines, or assumed details not present in the data.
- **Missing data → state it explicitly.** If a section has no supporting data, write "No data recorded." Do not fill the gap with plausible-sounding content.
- **Assumptions section is mandatory.** Any interpretation beyond a direct field read (e.g. deriving a blocker from stage logic, suggesting a move based on recruiter note wording) must be listed there, clearly labeled as an inference.

**My inputs (collect, confirm, or ask):**
- If **opportunity id** (or company + role) is **not** in memory, chat, or unambiguous from `opportunities.yaml`: **ask** before generating the report.
- If you infer **id** from company + role: state the resolved **id** and **ask the user to confirm or correct** before final output.
- Opportunity id (or company + role): `<...>`
