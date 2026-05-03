# Workflows & data — Career Path 2026

Functional scope, record schemas, and standard operating workflows. Loaded by Assistant tasks that touch career operations (JD/benchmark, planning, reviews, opportunity pipeline).

## Main functional scope

### A. Career Path Tracking
- Manage career milestones by phase (Now / Next / Later).
- Track milestone status:
  - Planned
  - In Progress
  - Blocked
  - Validated
  - Archived
- Track deadlines, completion evidence, and priority.

### B. Market Benchmark Intelligence
- Collect benchmarks from JD/role profile/job posts.
- Normalize benchmark format.
- Extract:
  - Must-have skills
  - Nice-to-have
  - Seniority
  - Domain/Industry
  - Responsibilities
  - Compensation band (if present)
  - Location/Work mode
- Compute fit score between personal profile and benchmark.
- Export capability gap reports to prioritize learning.

### C. Learning & Skill Sharpening
- Track learning path:
  - DSA
  - System Design (prefer cases with product trade-offs, ownership, reliability)
  - Coding
  - Problem Solving
  - AI/ML in production & AI-augmented engineering (per JD/gap needs)
- Map missing skills to target role and `career.direction_summary` in `master.yaml`.
- Suggest exercises and improvement plans weekly/daily.

### D. Planning & Review
- Weekly Plan (goals + actions + KPIs).
- Derive Daily Plan from Weekly Plan.
- End-of-day review and End-of-week review.
- Adjust career roadmap based on actual results.

## Core data to manage

### Career Milestone Record
- Milestone ID
- Target Role/Scope
- Time Horizon (Now/Next/Later)
- Success Criteria
- Baseline Level
- Target Level
- Evidence Link (sanitized)
- Priority (P0/P1/P2)
- Status
- Target Date
- Next Action
- Next Action Date
- Notes

### Market Benchmark Record
- Company Alias
- Role Title
- Source
- Benchmark Raw Input
- Benchmark Summary
- Required Skills
- Preferred Skills
- Gap Score (0-100)
- Priority (P0/P1/P2)
- Status (Reference/Active)
- Next Action
- Next Action Date
- Notes

### Personal Progress Record
- Week number / day
- Weekly/daily goals
- Active milestone count
- Completed milestone count
- Completed skill exercises
- Total focused learning hours
- Blockers
- Lessons learned
- Plan update

## Standard operating workflows

### Workflow 1: Benchmark Processing
1. Receive benchmark (JD/role profile/text/markdown/pdf/image OCR).
2. Normalize content.
3. Extract key information.
4. Produce short benchmark summary + skills table.
5. **Read candidate profile:** canonical source is `data/private/master.yaml` (headline, `career.direction_summary`, experience, skills, goals). If a separate CV/PDF exists, the user provides the path; `profile.resume` is optional. Extract only what is needed to compare to the JD; public reports are non-PII summaries only—do not copy email/phone/address into `reports/`.
6. Score gap/fit vs personal profile (resume + target metadata in `docs/framework/fit-weights.md`).
7. Assign priority + suggest learning actions.
8. Write to tracking report.

### Workflow 2: Career Decision
1. Summarize milestones and benchmarks (for fit/gap, read resume via `data/private/master.yaml` as in Workflow 1).
2. Compare on impact, growth, feasibility, interest, time horizon.
3. Recommend:
   - Execute now
   - Prepare foundation first
   - Defer
4. Generate action list for the next 24–72 hours.

### Workflow 3: Weekly Planning
1. Gather last week’s results.
2. Evaluate KPIs met/not met.
3. Pick 3–5 new weekly goals.
4. Break into daily tasks.
5. Set learning, practice, and review schedule.
6. Lock the plan and track execution.

### Workflow 4: Daily Review
1. Check today’s plan.
2. Mark done/pending.
3. Record feedback and blockers.
4. Update next action.
5. Prepare tomorrow’s plan.

## Opportunity Tracking (pipeline + reports)

**Data source:** `data/private/opportunities.yaml` (local, gitignored)—copy schema from `templates/opportunities_tracker_template.yaml`. Raw JDs live in `data/raw/`; optionally link `job_id` via `config/jd_catalog.csv`.

| Step | Task | Skill / template |
|:-----|:-----|:-----------------|
| 1 | Add opportunity from a JD file | `docs/skills/opportunity-from-jd/SKILL.md` |
| 2 | Update status/content (stage, next steps, notes, close deal) | `docs/skills/opportunity-update/SKILL.md` |
| 3 | Report tracked list | `docs/skills/opportunity-report-tracking/SKILL.md`, `templates/opportunity_report_tracking.md` |
| 4 | Next steps for **one** opportunity | `docs/skills/opportunity-report-next-steps-one/SKILL.md`, `templates/opportunity_report_next_steps_one.md` |
| 5 | **Rollup** next steps (sort by date → priority) | `docs/skills/opportunity-report-next-steps-rollup/SKILL.md`, `templates/opportunity_report_next_steps_rollup.md` |

**Reports with company names / sensitive detail:** default to `reports/private/` (gitignored). Public-safe excerpts → `reports/briefs/` after `docs/SANITIZATION_CHECKLIST.md`. Optional links: `milestone_id` with `data/career_path_master.csv`, `jd_source` with raw JD / catalog.
