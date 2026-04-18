# Prompt: report — opportunity tracking list (reuse)

Copy into a new chat. Replace bracketed fields.

---

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- `data/private/opportunities.yaml` (private)
- Output skeleton: `templates/opportunity_report_tracking.md`

**Task:**
1. Fill **Active pipeline** table: every item in `active` where `stage` is not `Closed` (or include Closed in a separate subsection if user asks).
2. Fill **Future desired** table from `future_desired` (include `next_action` columns if present).
3. Keep wording suitable for **`reports/private/`** (may contain real company names). For **`reports/briefs/`**, use aliases only and run `docs/SANITIZATION_CHECKLIST.md`.
4. Add **Assumptions** and **Risk**.

**Output:** Markdown ready to save as `reports/private/opportunity-tracking-<YYYY-MM-DD>.md` (path local / gitignored).

**Constraints:** No PII in public-bound copy; if user requests public summary, produce a second sanitized table.

---

**My inputs (fill in):**
- Include closed opportunities in appendix: `<yes | no | only counts>`

---
