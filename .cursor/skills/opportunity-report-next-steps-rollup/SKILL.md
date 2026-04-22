---
name: opportunity-report-next-steps-rollup
description: >-
  Builds a sorted rollup of next actions across all active opportunities using
  opportunity_report_next_steps_rollup template. Use when the user asks for
  combined backlog, rollup next steps, or sorted pipeline todos by date.
---

# Report — next steps rollup (all active)

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

**My inputs (collect, confirm, or ask):**
- If whether to **include future_desired** rows with `next_action` is **not** stated in chat or memory: **ask** (or propose a default and **ask for confirmation**).
- If you **infer** the choice from an earlier message: state it and **ask the user to confirm or correct** before final report.
- Include future_desired with next_action: `<yes | no>`
