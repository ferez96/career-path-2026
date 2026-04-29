---
name: jd-process
description: >-
  End-to-end JD processing workflow: normalize raw JD, research company, score fit/gap,
  generate analysis reports, and import to opportunity tracker. One-shot skill that orchestrates
  the full pipeline from data/raw → data/jds → reports → opportunities.yaml.
---

# JD Full Workflow

**Role:** Assistant — career operations (see `docs/AGENT_ROLES.md`).

**Purpose:** Drop a raw, non-normalized JD file and get complete analysis: normalized JD, company research, fit/gap scoring, reports, and opportunity entry ready to import.

**Context to load:**
- Raw JD file: `data/raw/<FILENAME>` (user provides filename)
- Master profile: `data/private/master.yaml` (for fit scoring)
- Fit/gap weights: `docs/cursor/fit-weights.md`
- JD analysis template: `templates/jd_analysis_template.md`
- Opportunity schema: `templates/opportunities_tracker_template.yaml`
- JD catalog: `config/jd_catalog.csv` (for existing IDs)
- Company-brief skill: `.cursor/skills/company-brief/SKILL.md` (for research sub-workflow)
- Opportunity-from-jd skill: `.cursor/skills/opportunity-from-jd/SKILL.md` (for import sub-workflow)

---

## Task: Full JD Workflow (10 steps)

### 1. Intake & Validation
- Confirm raw JD file exists in `data/raw/<FILENAME>`
- If file missing: ask user for correct filename
- Estimate file length (pages, word count for context budget)

### 2. JD Normalization
Read the raw JD and extract + structure key fields into a standardized markdown template:
- **Job Summary:** role_title, company_name, location, work_mode, level (e.g. IC3/Senior)
- **Key Responsibilities:** 3-5 bullet points from JD
- **Required Skills:** must-have technical skills (languages, frameworks, domains)
- **Nice-to-Have Skills:** preferred but not required
- **Qualifications:** years of experience, education, seniority expectations
- **Compensation & Benefits:** salary range (if visible), equity, benefits highlights
- **Team / Reporting:** team size, manager level, reporting structure

Save extracted data for slug creation and analysis.

### 3. Create Unique Slug
Generate a short, unique ID from:
- Company name (first 1-3 words, kebab-case)
- Role short name (e.g., "senior-backend" from "Senior Backend Engineer")
- Optional: date suffix (e.g., "-2026-04") if duplicates likely

Check `config/jd_catalog.csv` for existing IDs; suggest variant if slug exists.
Confirm slug with user before proceeding.

Example: `acme-senior-backend-2026-04`

### 4. Create Normalized JD File
Write normalized markdown to: `data/jds/{slug}.md`

**File structure:**
```
# {job_title} @ {company_name}

**Source:** data/raw/{original_filename}  
**Job ID:** {slug}  
**Date Processed:** {ISO date}  

## Job Summary
- Level: {level}
- Location: {location}
- Work Mode: {work_mode}
- Salary Range: {salary or "Not disclosed"}
- Team Size: {size}

## Key Responsibilities
{extracted bullets, max 5}

## Required Skills
{list with proficiency levels where apparent}

## Nice-to-Have Skills
{list}

## Qualifications
{seniority, years of experience, education}

## Compensation & Benefits
{highlights}

## Team Structure
{team, reporting, growth path}
```

### 5. Research Company (Sub-Workflow)
**Invoke `company-brief` skill with:**
- Company name (from normalized JD)
- Request scope: tier classification (startup/scale-up/FAANG/enterprise), size, product, reviews, engineering culture, DX, remote policy, AI/ML involvement
- Reference: user's profile from `master.yaml` for fit comparison

**Output from sub-workflow:**
- Full company brief (saved to `reports/private/{slug}-company-brief.md`)
- Tier classification
- Key risks / red flags
- Fit against master profile

### 6. Fit & Gap Scoring (Sub-Workflow)
Read the normalized JD + master profile, apply weights from `fit-weights.md`:

**Weights (by JD type):**
- If JD has AI/ML component:
  - Distributed systems & execution: 32%
  - System design & reliability: 22%
  - Systems-level ownership & cross-functional delivery: 18%
  - AI/ML in production: 5%
  - Domain & industry fit: 5%
  - Seniority match: 8%
  - Practical constraints (location/timezone/work mode): 10%

- If JD has NO AI/ML:
  - Redistribute 5% AI weight → Distributed systems (37%) and System design (27%)

**Output:**
- Scoring matrix: 0-100 per category
- Final fit score (0-100)
- Gap summary: which skills/domains need preparation
- Decision recommendation: Execute Now / Prepare Foundation First / Defer / Pass

### 7. Generate Analysis Reports

**7a. JD Analysis Report:** `reports/private/{slug}-analysis.md`
- Job snapshot (company, role, level, location)
- Skills extraction (required, nice-to-have)
- Fit/gap scoring table
- Gap summary + preparation path
- Decision recommendation
- 48-hour action plan (if pursuing)

**7b. Company Brief:** `reports/private/{slug}-company-brief.md`
(From sub-workflow above)

**7c. Combined Decision Brief:** `reports/private/{slug}-decision.md`
- 1-page executive summary
- Company fit + opportunity fit
- Recommendation (Pursue / Prepare / Defer / Pass)
- Top 3 next steps (24-72h)
- Key assumptions & risks

### 8. Import to Opportunity Tracker (Sub-Workflow)
**Invoke `opportunity-from-jd` skill with:**
- Normalized JD data (from step 2)
- Slug (from step 3)
- Reference to normalized file: `data/jds/{slug}.md`
- Fit score from step 6 (add as note: "Fit score: {score}/100")

**Output from sub-workflow:**
- YAML snippet for `opportunities.yaml`
- Optional CSV row for `jd_catalog.csv`

### 9. Update JD Catalog
Add or update `config/jd_catalog.csv` with row:
```
job_id,alias,role,company,raw_path,normalized_path,status,date_processed
{slug},"{slug}",{role_title},{company_name},data/raw/{filename},data/jds/{slug}.md,new,{ISO date}
```

### 10. Summarize & Output Checklist
Provide user with complete checklist:
```
✅ JD normalized: data/jds/{slug}.md
✅ Company brief: reports/private/{slug}-company-brief.md
✅ Fit analysis: reports/private/{slug}-analysis.md
✅ Decision brief: reports/private/{slug}-decision.md
✅ Opportunity YAML snippet (ready to insert)
✅ Catalog CSV row (ready to insert)

Next Steps:
1. Review analysis reports (private/)
2. Confirm opportunity YAML (id, stage, priority, next_action)
3. Insert YAML into data/private/opportunities.yaml
4. Insert CSV row into config/jd_catalog.csv
5. When ready to publish: run sanitization checklist → copy briefs to reports/briefs/
```

---

## Inputs (collect, confirm, or ask)

**Required (ask if not provided):**
- Path to raw JD: `data/raw/<FILENAME>` — confirm file exists
- Company name (disambiguation if needed): used for slug + company-brief scope

**Optional (user may override):**
- Initial opportunity stage: default `Interested` (or `Applied` if already submitted)
- Priority: default `P1` (or `P0`/`P2` if user specifies)
- Next action: auto-suggested from analysis; confirm with user

---

## Output sections

1. **Normalized JD** (markdown file)
2. **Company Brief** (markdown report)
3. **JD Analysis** (markdown report with scores)
4. **Decision Brief** (1-page summary)
5. **Opportunity YAML** (snippet to paste)
6. **Catalog CSV** (row to insert)
7. **Assumptions / Risk**
8. **Checklist** (what was created, what to do next)

---

## Constraints

- **No PII in public outputs:** All private reports go to `reports/private/` (gitignored). Sanitize before copying to `reports/briefs/`.
- **Data classification:**
  - `data/raw/{filename}` → `raw-ingest` (ignore, do not commit)
  - `data/jds/{slug}.md` → `derived-sanitized` (track after sanitization)
  - `reports/private/{slug}-*.md` → `private-sensitive` (ignore, do not commit)
- **Do not fabricate.** This applies to every step: role extraction, company research, fit scoring, action plans, and next steps. Only use information explicitly present in the JD file, `master.yaml`, or stated by the user.
  - Missing JD fields (salary, team size, work mode, etc.) → `"Not disclosed"` or `"Unknown"`. Do not guess.
  - Fit scoring rationale must cite specific JD text or profile data. Do not invent supporting evidence.
  - Action plans and next steps (Steps 7a, 7c) must be grounded in the analysis output. Do not add generic career advice not derived from the data.
  - All inferences must be listed in the **Assumptions / Risk** output section (Step 7c and final checklist).
  - The `company-brief` sub-workflow inherits its own no-fabrication rules (fact / inference / unknown labeling per claim).
- **Opportunity ID collision:** Check `config/jd_catalog.csv` for existing slugs; ask before override.

---

## Sub-Workflows (Reuse Existing Skills)

### company-brief sub-workflow
Skill: `.cursor/skills/company-brief/SKILL.md`
- Input: company name, optional profile context
- Output: full brief markdown with tier, culture, fit analysis
- Saves to: `reports/private/{slug}-company-brief.md`

### opportunity-from-jd sub-workflow
Skill: `.cursor/skills/opportunity-from-jd/SKILL.md`
- Input: normalized JD data (role, company, level, fit score)
- Output: YAML snippet + optional catalog CSV row
- User confirms before insertion into `opportunities.yaml`

---

## Success Criteria

✅ All 4 reports generated in `reports/private/`  
✅ Opportunity YAML ready to import (no duplicates in opportunities.yaml)  
✅ Catalog CSV row ready to insert  
✅ Checklist provided to user  
✅ All files classified correctly (raw-ingest / derived-sanitized / private-sensitive)  
✅ Next steps clear and actionable (24-72h horizon)
