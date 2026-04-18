# Prompt: report — next steps for one opportunity (reuse)

Copy into a new chat. Replace bracketed fields.

---

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- `data/private/opportunities.yaml` (private)
- Output skeleton: `templates/opportunity_report_next_steps_one.md`

**Task:**
1. Select the record by **`id`**: `<OPPORTUNITY_ID>` (or company + role if user specifies — resolve ambiguity).
2. Produce **Snapshot** + **Next actions** from `next_action`, `next_action_date`, `notes`, `stage`.
3. Add **Blockers / risks** from notes and stage.
4. Add **Suggested 24–72h moves** aligned with `CURSOR.md` execution style.
5. **Assumptions** / **Risk**.

**Output:** Markdown for `reports/private/opportunity-next-steps-<id>-<YYYY-MM-DD>.md` or paste-only.

**Constraints:** Full detail stays private; sanitize before any public `reports/briefs/` excerpt.

---

**My inputs (fill in):**
- Opportunity id (or company + role): `<...>`

---
