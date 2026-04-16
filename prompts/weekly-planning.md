# Prompt: next-week planning (reuse)

Copy everything inside the fence into a new chat (adjust bracketed fields).

---

**Role:** Assistant — career / execution (see `docs/AGENT_ROLES.md`).

**Context to load (if available):**
- `data/private/master.yaml` (private; no PII in any public-bound output)
- `config/context_manifest.yaml`
- Previous week file: `data/weekly/<PREV_ISO_WEEK>.md` (e.g. `2026-W16.md`)

**Task:**
1. Propose a **weekly plan** for **ISO week `<YYYY-Www>`**, covering **`<Mon>`–`<Sun>`** (or only **remaining days** if mid-week).
2. Align with: active job search, `target_employment_horizon`, remote-first / HCMC, salary expectations, deal-breakers, domain priorities from `master.yaml`.
3. Output should be **ready to paste** into `data/weekly/<YYYY-Www>.md`, following the structure of `templates/weekly_plan_template.md` and the style of the previous week file (Focus checklist, KPI table, daily log, risks).
4. Include **measurable KPIs** (outbound count, shortlist size, mock sessions, etc.) and **Assumptions** / **Risk** if any input is missing.

**My inputs this week (fill in):**
- Fixed commitments / travel: `<...>`
- Interviews or recruiter calls already scheduled: `<dates or "none">`
- What worked / failed last week (one line each): `<...>`
- Priority shift vs last week: `<same | more volume | more prep | ...>`

**Constraints:**
- No PII in content intended for public `reports/`.
- Prefer product / in-house roles; respect outsource deal-breaker from `master.yaml`.

---
