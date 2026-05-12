---
name: jd-process
description: >-
  End-to-end JD processing workflow: normalize raw JD, research company, score fit/gap,
  generate analysis reports, and import to opportunity tracker. One-shot skill that orchestrates
  the full analysis and opportunity import.
---

# JD Full Workflow

**Role:** Assistant — career operations (see `docs/AGENT_ROLES.md`).

**Purpose:** Drop a raw, non-normalized JD file and get complete analysis: normalized JD, company research, fit/gap scoring, reports, and opportunity entry ready to import.

**Context to load:**
- JD file: paste text or path (user provides)
- Master profile: `data/master.yaml` (for fit scoring)
- Fit/gap weights: `docs/framework/fit-weights.md`
- JD analysis template: `templates/jd_analysis_template.md`
- Opportunity schema: `templates/opportunities_tracker_template.yaml`
- JD catalog: `config/jd_catalog.csv` (for existing IDs)

**Scope:**
- Load only the required templates, profiles, and reference docs.
- Do not load unrelated working notes or prior reports unless the user explicitly asks.

---

## Task: Full JD Workflow (10 steps)

### 1. Intake & Validation
- Confirm JD file or text is available (user pastes or provides path)
- If file is a path, verify it exists
- Estimate file length (pages, word count for context budget)

### 2. JD Normalization
Read the raw JD and extract + structure key fields into a standardized markdown template:
- **Job Summary:** role_title, company_name, location, work_mode, level (e.g. IC3/Senior)
- **If company name is not stated in the JD:** do not guess. Stop and ask the user: *"Company name not found in JD — please provide a label or alias to use (e.g. 'sf-startup', 'unknown-fintech')."* Do not proceed to Step 3 until a label is confirmed.
- **Key Responsibilities:** 3-5 bullet points from JD
- **Required Skills:** must-have technical skills (languages, frameworks, domains)
- **Nice-to-Have Skills:** preferred but not required
- **Qualifications:** years of experience, education, seniority expectations
- **Compensation & Benefits:** salary range (if visible), equity, benefits highlights
- **Team / Reporting:** team size, manager level, reporting structure

Save extracted data for slug creation and analysis.

### 3. Create Unique Slug

**Slug formula:** `{company}-{role}-{team?}-{level?}-{date?}`

**Token rules:**
- **`company`** (required): first 1-3 words of the company name, kebab-case. Examples: `acme`, `goldman-sachs`.
- **`role`** (required): short role token. Examples: `backend`, `data-platform`, `ml-infra`. Drop generic suffixes like "Engineer" / "Developer" *after* the level token is decided.
- **`level`** (required when the JD title contains one): `junior` / `mid` / `senior` / `staff` / `principal`. **Never strip this during shortening** (so `Senior Backend Engineer` and `Backend Engineer` never collide).
- **`team`** (required when the JD names a specific team, product line, or sub-domain, or when the same company is likely to have multiple roles at the same role+level): 1-2 kebab tokens. Examples: `platform`, `risk`, `search`, `payments`.
- **`date`** (required only for re-opens, see below): `YYYY-MM` of the new posting. Do **not** use for first-time slugs.

**Catalog check (prefix scan, not exact match):**
1. Scan `config/jd_catalog.csv` for every `job_id` starting with `{company}-`.
2. List all matches to the user with their `role`, `status`, and `date_processed`.
3. Ask: *"Is this a **new role**, a **re-post** of an open role, or a **re-open** of a closed one?"*
   - **New role:** add `team` and/or `level` tokens until the slug is unique. No date suffix.
   - **Re-post (same role, still open):** reuse the existing slug. Do not create a new JD file or opportunity; route the user to the `opportunity-update` skill instead and exit the JD workflow.
   - **Re-open (previously closed):** append `-YYYY-MM` to the existing slug to disambiguate. Create a new opportunity entry whose `notes` references the old `id` (e.g. `"Re-open of acme-senior-backend; previously closed 2026-02"`).
4. Confirm the final slug with the user before proceeding to Step 4.

**Examples:**
- `acme-senior-backend` (only one Acme role known)
- `acme-senior-backend-platform` (second Acme role, same level, different team)
- `acme-staff-backend-platform` (third Acme role, different level, same team)
- `acme-senior-backend-platform-2026-05` (re-open of a previously closed Acme platform role)

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

**If company name is unknown (user provided only an alias):** skip this step entirely. Note in Assumptions: "Company-brief skipped, company identity not disclosed in JD." Proceed to Step 6.

**If company name is known:** check for an existing brief before invoking the sub-workflow.

**Brief reuse check (multi-role-per-company optimization):**
1. Look for prior briefs in this order:
   - Canonical shared brief: `data/reports/companies/{company-slug}.md`
   - Any `data/reports/roles/*-company-brief.md` whose `company_display` matches the JD
2. If a brief exists and is **less than 90 days old**: reuse it. Reference its path in this role's report set; do **not** regenerate.
3. If a brief exists but is **90 days old or older**: ask the user *"Reuse the existing brief (dated {YYYY-MM-DD}) or refresh?"*. Only invoke the sub-workflow on `refresh`.
4. If no prior brief exists: invoke the sub-workflow and save the canonical output to `data/reports/companies/{company-slug}.md`.

**Invoke `company-brief` skill with:**
- Company name (from normalized JD)
- Request scope: tier classification (startup/scale-up/FAANG/enterprise), size, product, reviews, engineering culture, DX, remote policy, AI/ML involvement
- Reference: user's profile from `master.yaml` for fit comparison

**Output from sub-workflow:**
- Canonical company brief saved to `data/reports/companies/{company-slug}.md` (shared across roles)
- Optional role-specific delta at `data/reports/roles/{slug}-company-brief.md`, written **only if** the role context materially changes the fit story
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

### 7. Import to Opportunity Tracker (Sub-Workflow)
**Invoke `opportunity-from-jd` skill with:**
- Normalized JD data (from step 2)
- Slug (from step 3)
- Reference to normalized file: `data/jds/{slug}.md`
- Fit score from step 6 (add as note: "Fit score: {score}/100")

**Output from sub-workflow:**
- YAML snippet for `opportunities.yaml`
- Optional CSV row for `jd_catalog.csv`

### 8. Update JD Catalog
Add or update `config/jd_catalog.csv` with row:
```
job_id,alias,role,company,raw_path,normalized_path,status,date_processed
{slug},"{slug}",{role_title},{company_name},data/raw/{filename},data/jds/{slug}.md,new,{ISO date}
```

### 9. Summarize & Output Checklist
Provide user with checklist of core deliverables produced so far:
```
✅ JD normalized: data/jds/{slug}.md
✅ Company brief: data/reports/companies/{company-slug}.md (canonical; reused or generated in Step 5)
   └── role delta (if any): data/reports/roles/{slug}-company-brief.md
✅ Opportunity YAML snippet (ready to insert)
✅ Catalog CSV row (ready to insert)
⏸ Analysis reports: pending user choice (see Step 10)

Next Steps:
1. Confirm opportunity YAML (id, stage, priority, next_action)
2. Insert YAML into data/private/opportunities.yaml
3. Insert CSV row into config/jd_catalog.csv
4. Decide on analysis reports in Step 10 (optional)
```

### 10. Generate Analysis Reports (Optional)
**Ask the user:** *"Would you like me to generate analysis reports? Choose one:*
- ***A)** All 3 reports (JD Analysis + Company Brief + Decision Brief)*
- ***B)** Decision Brief only (1-page executive summary)*
- ***C)** Skip, no reports needed*"*

Wait for the user's choice before generating anything.

**If A (all 3 reports):** generate 10a, 10b, and 10c below.
**If B (Decision Brief only):** generate 10c only.
**If C (skip):** confirm skip; scoring output from Step 6 remains available in session only. End workflow.

---

**10a. JD Analysis Report:** `data/reports/roles/{slug}-analysis.md`
- Job snapshot (company, role, level, location)
- Skills extraction (required, nice-to-have)
- Fit/gap scoring table
- Gap summary + preparation path
- Decision recommendation
- 48-hour action plan (if pursuing)

**10b. Company Brief:** `data/reports/companies/{company-slug}.md` (canonical), plus optional `data/reports/roles/{slug}-company-brief.md` (role delta).
(Already produced or reused by the `company-brief` sub-workflow in Step 5 if company was known. Reference both paths and surface in the final checklist; do not regenerate here.)

**10c. Combined Decision Brief:** `data/reports/roles/{slug}-decision.md`
- 1-page executive summary
- Company fit + opportunity fit
- Recommendation (Pursue / Prepare / Defer / Pass)
- Top 3 next steps (24-72h)
- Key assumptions & risks

After generation, append generated paths to the Step 9 checklist and re-output the updated checklist to the user.

---

## Inputs (collect, confirm, or ask)

**Required (ask if not provided):**
- Path to raw JD: `data/raw/<FILENAME>` — confirm file exists
- Company name or alias: used for slug + company-brief scope. If not in JD, ask user for a short label (e.g. `sf-startup`, `unknown-fintech`). Do not proceed without this.

**Optional (user may override):**
- Initial opportunity stage: default `Interested` (or `Applied` if already submitted)
- Priority: default `P1` (or `P0`/`P2` if user specifies)
- Next action: auto-suggested from analysis; confirm with user

---

## Output sections

1. **Normalized JD** (markdown file)
2. **Company Brief** (markdown report, from Step 5 if company is known)
3. **Opportunity YAML** (snippet to paste)
4. **Catalog CSV** (row to insert)
5. **Assumptions / Risk**
6. **Checklist** (what was created, what to do next)
7. **JD Analysis** (markdown report with scores) *(optional, Step 10)*
8. **Decision Brief** (1-page summary) *(optional, Step 10)*

---

## Constraints

- **Vault vs public:** Role reports go to `data/reports/roles/` (private). **`data/**` does not require PII sanitization** for personal use.
- **Data classification:**
  - `data/raw/{filename}` → `raw-ingest` (ignore, do not commit)
  - `data/jds/{slug}.md` → `private-sensitive` (local vault; typically gitignored with rest of `data/`)
  - `data/reports/roles/{slug}-*.md` → `private-sensitive` (ignore, do not commit)
  - `data/reports/companies/{company-slug}.md` → `private-sensitive` (shared per-company brief; ignore, do not commit)
- **Do not fabricate.** This applies to every step: role extraction, company research, fit scoring, action plans, and next steps. Only use information explicitly present in the JD file, `master.yaml`, or stated by the user.
  - Missing JD fields (salary, team size, work mode, etc.) → `"Not disclosed"` or `"Unknown"`. Do not guess.
  - Fit scoring rationale must cite specific JD text or profile data. Do not invent supporting evidence.
  - Action plans and next steps (Steps 10a, 10c) must be grounded in the analysis output. Do not add generic career advice not derived from the data.
  - All inferences must be listed in the **Assumptions / Risk** output section (Step 10c and final checklist).
  - The `company-brief` sub-workflow inherits its own no-fabrication rules (fact / inference / unknown labeling per claim).
- **Opportunity ID collision:** Check `config/jd_catalog.csv` for existing slugs; ask before override.

---

## Sub-Workflows (Reuse Existing Skills)

### company-brief sub-workflow
Skill: `docs/skills/company-brief/SKILL.md`
- Input: company name, optional profile context
- Output: full brief markdown with tier, culture, fit analysis
- Saves to: canonical `data/reports/companies/{company-slug}.md`; optional role delta `data/reports/roles/{slug}-company-brief.md` (see Step 5)

### opportunity-from-jd sub-workflow
Skill: `docs/skills/opportunity-from-jd/SKILL.md`
- Input: normalized JD data (role, company, level, fit score)
- Output: YAML snippet + optional catalog CSV row
- User confirms before insertion into `opportunities.yaml`

---

## Success Criteria

✅ Normalized JD saved to `data/jds/{slug}.md`  
✅ Company brief produced (Step 5) when company is known  
✅ Opportunity YAML ready to import (no duplicates in opportunities.yaml)  
✅ Catalog CSV row ready to insert  
✅ Checklist provided to user  
✅ User explicitly prompted in Step 10 for optional reports (A / B / C); chosen reports generated under `data/reports/roles/`  
✅ All files classified correctly (raw-ingest vs `data/**` private vault vs public-bound `derived-sanitized` if any)  
✅ Next steps clear and actionable (24-72h horizon)
