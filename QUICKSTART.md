# Quick start (job search)

**What this is:** one place for your profile, applications, JDs, and plans — see [README.md](README.md).

---

## Step 1 — Install

From the **root of the repository**, run **one** of the following commands to set up required folders and install the starter templates:

```powershell
pwsh -File scripts/bootstrap.ps1
```

```bash
bash scripts/bootstrap.sh
```

This will generate the initial directory structure (`data/*`, `reports/*`, etc.) and copy the template files listed below **only if the target does not already exist** (no overwrite):

| Template                                   | Installed path                          |
|:--------------------------------------------|:----------------------------------------|
| `templates/opportunities_tracker_template.yaml` | `data/private/opportunities.yaml`       |
| `templates/master_template.yaml`                | `data/private/master.yaml`              |
| `templates/jd_catalog_template.csv`             | `config/jd_catalog.csv`                 |
| `templates/weekly_plan_template.md`             | `data/weekly/weekly-plan-TEMPLATE.md`   |
| `templates/daily_review_template.md`            | `data/daily/daily-review-TEMPLATE.md`   |

---

## Step 2 — Fill `master.yaml`

Edit **`data/private/master.yaml`** (created in step 1). 

Quickest: provide your AI agent with either a resume file or a short plaintext bio, and have it extract and fill in the key YAML fields (headline, `career.direction_summary`, targets, skills, experience) using only information you supplied—no invented details. See guidance for fit/gap and public output in [`.cursor/rules/career-path-resume.mdc`](.cursor/rules/career-path-resume.mdc).

---

## Step 3 — Add an opportunity (JD)

1. Save the JD text or file under **`data/raw/`** (e.g. `data/raw/acme-backend.md`).
2. Open **`.cursor/skills/opportunity-from-jd/SKILL.md`** (or invoke the **opportunity-from-jd** Cursor skill) with your Assistant, including the JD and context from **`data/private/master.yaml`**.
3. Update **`data/private/opportunities.yaml`** when you move stages or set next actions (or use **`.cursor/skills/opportunity-update/SKILL.md`** / skill **opportunity-update**).

---

## Step 4 — Weekly and daily plan

1. **Weekly** — Open **`.cursor/skills/weekly-planning/SKILL.md`** (or skill **weekly-planning**), set the ISO week and your inputs, run with your Assistant. Save the result as **`data/weekly/<YYYY-Www>.md`** (you can start from `data/weekly/weekly-plan-TEMPLATE.md` or rename/copy it).
2. **Daily** — Use **`data/daily/daily-review-TEMPLATE.md`** as a base for **`data/daily/YYYY-MM-dd-daily-review.md`**, or ask your Assistant to break the current weekly plan into today’s checklist using **`templates/daily_review_template.md`**.

---

## More later

Sanitized reports, benchmarks, briefs, publishing to `public`, and the full prompt list live in **[CURSOR.md](CURSOR.md)** (and its chunked framework under `docs/cursor/`) and the sections below.

### Where things live

| Need | Location |
|:-----|:---------|
| Profile (fit/gap) | `data/private/master.yaml` |
| Application pipeline | `data/private/opportunities.yaml` |
| Raw JD paste / files | `data/raw/` |
| Optional JD index | `config/jd_catalog.csv` |
| Sanitized JD analysis | `reports/benchmarks/` |
| Sanitized briefs | `reports/briefs/` |
| Sensitive / full detail | `reports/private/` |

Full tree: [docs/REPO_LAYOUT.md](docs/REPO_LAYOUT.md).

### Other opportunity skills

| Goal | Open |
|:-----|:-----|
| Update stage, notes, or close | `.cursor/skills/opportunity-update/SKILL.md` |
| Full tracking list | `.cursor/skills/opportunity-report-tracking/SKILL.md` |
| Next steps (one role / rollup) | `.cursor/skills/opportunity-report-next-steps-one/SKILL.md`, `.cursor/skills/opportunity-report-next-steps-rollup/SKILL.md` |

Stable links under `prompts/*.md` redirect to the same `SKILL.md` files.

### Before you publish to `public`

Flow: **`personal` → sanitize → `public` (`master`)**. Only non-PII, sanitized content on public.

- [docs/BRANCH_WORKFLOW.md](docs/BRANCH_WORKFLOW.md)
- [docs/PUBLIC_REPO_POLICY.md](docs/PUBLIC_REPO_POLICY.md)
- [docs/SANITIZATION_CHECKLIST.md](docs/SANITIZATION_CHECKLIST.md)
- [docs/DATA_CLASSIFICATION.md](docs/DATA_CLASSIFICATION.md)

### Agent roles

**Copilot** = framework and repo; **Assistant** = analysis and planning runs. [docs/AGENT_ROLES.md](docs/AGENT_ROLES.md).

### Read next

- **[CURSOR.md](CURSOR.md)** — Operating framework index → `docs/cursor/{workflows,fit-weights,prompting,cadence}.md`.
- **[reports/README.md](reports/README.md)** — `benchmarks/` vs `briefs/` vs `private/`.
- **[config/context_manifest.yaml](config/context_manifest.yaml)** — Agent context index.
