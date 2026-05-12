---
name: opportunity-report-tracking
description: >-
  Builds the full opportunity pipeline markdown report from opportunities.yaml
  using opportunity_report_tracking template. Use when the user asks for tracking
  list report, pipeline snapshot, or opportunity-tracking markdown output.
---

# Report — opportunity tracking list

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- `data/opportunities.yaml`
- Output skeleton: `templates/opportunity_report_tracking.md`

**Scope:**
- Read only the tracker YAML and prior snapshots if comparing. Avoid reading unrelated artifacts.

**Task:**
1. Fill **Active pipeline** table: every item in `active` where `stage` is not `Closed` (or include Closed in a separate subsection if user asks).
2. Fill **Future desired** table from `future_desired` (include `next_action` columns if present).
3. Keep wording suitable for **`data/reports/pipeline/`** (full-detail tracking; gitignored, so real company names are fine).
4. Add **Assumptions** and **Risk**.

**Output:** Markdown ready to save as `data/reports/pipeline/opportunity-tracking-<YYYY-MM-DD>.md` (path local / gitignored).

**Constraints:**
- No PII in public-bound copy; if user requests public summary, produce a second sanitized table.
- **Do not fabricate.** Table cells must reflect field values exactly as stored. If a field is absent or empty, write "—" in the cell. Do not substitute guesses or defaults.

**My inputs (collect, confirm, or ask):**
- If whether to **include closed** in the appendix is **not** stated in chat or memory: **ask** (or propose a default such as `no` and **ask for confirmation**).
- If you **infer** the choice from an earlier message: state it and **ask the user to confirm or correct** before final report.
- Include closed opportunities in appendix: `<yes | no | only counts>`
