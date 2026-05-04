---
name: weekly-planning
description: >-
  Proposes an ISO-week job-search execution plan from master.yaml, prior weekly
  files, and weekly_plan_template. Use when the user asks for weekly planning,
  next ISO week KPIs, data/weekly preparation, or mid-week remaining-days plan.
---

# Weekly planning

**Role:** Assistant — career / execution (see `docs/AGENT_ROLES.md`).

**Context to load (if available):**
- `data/private/master.yaml` (private; no PII in any public-bound output)
- `config/context_manifest.yaml`
- Previous week file: `data/weekly/<PREV_ISO_WEEK>.md` (e.g. `2026-W16.md`)

**Task:**
1. Propose a **weekly plan** for **ISO week `<YYYY-Www>`**, covering **`<Mon>`–`<Sun>`** (or only **remaining days** if mid-week).
2. Align with: active job search, `target_employment_horizon`, `career.direction_summary` and `target_titles`, remote-first / HCMC, salary expectations, deal-breakers, domain priorities from `master.yaml`.
3. Output should be **ready to paste** into `data/weekly/<YYYY-Www>.md`, following the structure of `templates/weekly_plan_template.md` and the style of the previous week file (Focus checklist, KPI table, daily log, risks).
4. Include **measurable KPIs** (outbound count, shortlist size, mock sessions, etc.) and **Assumptions** / **Risk** if any input is missing.

**My inputs this week (collect, confirm, or ask):**
- If the following are **not** already known from memory, prior messages, or repo files (`data/weekly/*.md`, chat): **ask the user** for each missing item before locking the plan.
- If you **infer** any item from context (memory, last week file, earlier chat): state it in one line per bullet and **ask the user to confirm or correct** before producing the final paste-ready weekly file.
- Fixed commitments / travel: `<...>`
- Interviews or recruiter calls already scheduled: `<dates or "none">`
- What worked / failed last week (one line each): `<...>`
- Priority shift vs last week: `<same | more volume | more prep | ...>`

**Constraints:**
- No PII in content intended for public `reports/`.
- Prefer product / in-house roles; respect outsource deal-breaker from `master.yaml`.
