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
3. Add **Blockers / risks** from notes and stage.
4. Add **Suggested 24–72h moves** aligned with the workflow style in `docs/cursor/workflows.md` (Workflow 2).
5. **Assumptions** / **Risk**.

**Output:** Markdown for `reports/private/opportunity-next-steps-<id>-<YYYY-MM-DD>.md` or paste-only.

**Constraints:** Full detail stays private; sanitize before any public `reports/briefs/` excerpt.

**My inputs (collect, confirm, or ask):**
- If **opportunity id** (or company + role) is **not** in memory, chat, or unambiguous from `opportunities.yaml`: **ask** before generating the report.
- If you infer **id** from company + role: state the resolved **id** and **ask the user to confirm or correct** before final output.
- Opportunity id (or company + role): `<...>`
