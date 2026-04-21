# Project: Career Path 2026

## 1) Project goals

Career Path 2026 is a personal system to:
- Design long-term career stages (6–12–24 months), **prioritizing systems-level ownership, plus AI/ML in production and AI-augmented tooling to improve delivery** (details in `data/private/master.yaml` → `career.direction_summary`, `profile.headline`).
- Track capability progress and execution outcomes weekly/monthly.
- Plan and review on a weekly/daily cadence.
- Collect and normalize benchmarks from roles/JDs as reference data (applying immediately is optional).
- Produce capability gap reports to guide learning and growth.
- Combine skill sharpening (DSA, System Design, Coding, Problem Solving) with career planning.

## 2) Language

- **Repository default:** English-first (docs, templates, prompts, and structured outputs in this repo).
- **Chat with your agent:** You may use Vietnamese (or another language) when talking to the assistant; the assistant should follow your language in conversation while keeping **repo artifacts** (files under `docs/`, `templates/`, `prompts/`, `reports/` when shared publicly) aligned with English-first unless you ask otherwise.

## 3) Supported file formats

**Input:**
- Markdown
- Plaintext
- PDF
- PNG (OCR if text is present)

**Output:**
- Markdown (reports, plans, reviews)
- Plaintext (quick notes)
- CSV/Markdown tables (tracking)
- PDF (optional, final export)

## 4) Target Metadata

```yaml
target_profile:
  primary_role: "Distributed Systems Engineer"
  fallback_role:
    allowed: true
    role: "Senior Software Engineer (Backend / Distributed Systems)"
    company_tier_condition: "FAANG+"
  preferred_company_tiers:
    - "Tier-1"
    - "FAANG+"
  editable_for_publish: true
```

## 5) Main functional scope

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

## 6) Core data to manage

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

## 7) Standard operating workflows

### Workflow 1: Benchmark Processing
1. Receive benchmark (JD/role profile/text/markdown/pdf/image OCR).
2. Normalize content.
3. Extract key information.
4. Produce short benchmark summary + skills table.
5. **Read candidate profile:** canonical source is `data/private/master.yaml` (headline, `career.direction_summary`, experience, skills, goals). If a separate CV/PDF exists, the user provides the path; `profile.resume` is optional. Extract only what is needed to compare to the JD; public reports are non-PII summaries only—do not copy email/phone/address into `reports/`.
6. Score gap/fit vs personal profile (resume + target metadata in this file).
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

### Opportunity Tracking (pipeline + reports)

**Data source:** `data/private/opportunities.yaml` (local, gitignored)—copy schema from `templates/opportunities_tracker_template.yaml`. Raw JDs live in `data/raw/`; optionally link `job_id` via `config/jd_catalog.csv`.

| Step | Task | Prompt / template |
|:-----|:-----|:------------------|
| 1 | Add opportunity from a JD file | `prompts/opportunity-from-jd.md` |
| 2 | Update status/content (stage, next steps, notes, close deal) | `prompts/opportunity-update.md` |
| 3 | Report tracked list | `prompts/opportunity-report-tracking.md`, `templates/opportunity_report_tracking.md` |
| 4 | Next steps for **one** opportunity | `prompts/opportunity-report-next-steps-one.md`, `templates/opportunity_report_next_steps_one.md` |
| 5 | **Rollup** next steps (sort by date → priority) | `prompts/opportunity-report-next-steps-rollup.md`, `templates/opportunity_report_next_steps_rollup.md` |

**Reports with company names / sensitive detail:** default to `reports/private/` (gitignored). Public-safe excerpts → `reports/briefs/` after `docs/SANITIZATION_CHECKLIST.md`. Optional links: `milestone_id` with `data/career_path_master.csv`, `jd_source` with raw JD / catalog.

## 8) Fit Score Weights (experimental)

Emphasis on **systems ownership + AI in delivery**; when the JD has no AI/ML, redistribute the AI percentage into *Distributed systems* and *System design*.

- Distributed systems & backend execution: 32%
- System design & scalability / reliability: 22%
- Systems-level product ownership & cross-functional delivery: 18%
- AI/ML in production or AI-augmented engineering (when the JD includes this): 5% — if not, add to the first two buckets
- Domain & industry fit: 5%
- Seniority match: 8%
- Practical constraints (location/timezone/work mode): 10%

## 9) Suggested KPIs

### Career Path KPI
- Benchmarks collected / week
- Active milestones / week
- Milestones validated / month
- Share of milestones completed on time
- Capability evidence updates

### Learning KPI
- Focused learning hours / week
- DSA problems completed
- Mock interviews
- System Design topics completed (prefer cases with **product trade-offs**, multi-team ownership, SLO/incident narrative)
- Time or exercises on **AI/ML in production** (serving, evaluation, cost/latency, data pipelines)—when the weekly roadmap includes it
- **AI-augmented workflow** experiments (review, codegen, test) with evidence (short notes, no PII)
- Repeat mistakes addressed

### Execution KPI
- % daily plan completed
- % weekly goals completed
- Blockers open > 7 days

## 10) Prompting Rules (for AI Assistant)

- Follow docs/SANITIZATION_CHECKLIST.md
- Do not invent company/JD facts.
- If data is missing, clarify before concluding.
- Prefer structured tables/checklists.
- Always include:
  - Main insight
  - Recommended actions
  - Next step within 24h
- Every report must have **Assumptions** and **Risk**.

## 11) Suggested operating cadence

- Monday: Weekly planning + milestone prioritization
- Tue–Thu: Focused learning + hands-on practice
- Friday: Deep review + progress tracking + plan adjustment
- Saturday: Mock interview / portfolio hardening / system design review
- Sunday: Light wrap-up and prep for the new week
