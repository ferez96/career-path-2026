# Prompt: report — next steps rollup (all active) (reuse)

Copy into a new chat. Replace bracketed fields.

---

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- `data/private/opportunities.yaml` (private)
- Output skeleton: `templates/opportunity_report_next_steps_rollup.md`

**Task:**
1. Collect **next_action** for every item in `active` with `stage` not `Closed` (unless user wants closed included).
2. Optionally include **`future_desired`** entries that have **`next_action`** set.
3. **Sort** rows: primary `next_action_date` ascending (empty dates last); secondary `priority` P0 → P1 → P2.
4. Build **Combined backlog** table; each row must include **`opportunity_id`** for traceability.
5. **Assumptions** / **Risk**.

**Output:** Markdown for `reports/private/opportunity-next-steps-rollup-<YYYY-MM-DD>.md` or paste-only.

**Constraints:** Private report may use real names; public summary requires sanitization.

---

**My inputs (fill in):**
- Include future_desired with next_action: `<yes | no>`

---
