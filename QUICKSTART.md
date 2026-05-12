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

This will generate the initial directory structure (`data/*`, including `data/reports/*`, etc.) and copy the template files listed below **only if the target does not already exist** (no overwrite):

| Template                                   | Installed path                          |
|:--------------------------------------------|:----------------------------------------|
| `templates/opportunities_tracker_template.yaml` | `data/opportunities.yaml`               |
| `templates/master_template.yaml`                | `data/master.yaml`                      |
| `templates/jd_catalog_template.csv`             | `config/jd_catalog.csv`                 |
| `templates/weekly_plan_template.md`             | `data/weekly/weekly-plan-TEMPLATE.md`   |
| `templates/daily_review_template.md`            | `data/daily/daily-review-TEMPLATE.md`   |

---

## Step 2 — Fill `master.yaml`

Edit **`data/master.yaml`** (created in step 1). 

Quickest: provide your AI agent with either a resume file or a short plaintext bio, and have it extract and fill in the key YAML fields (headline, `career.direction_summary`, targets, skills, experience) using only information you supplied—no invented details. See guidance in [`docs/rules/career-path-resume.md`](docs/rules/career-path-resume.md).

---

## Step 3 — Add an opportunity (JD)

1. Save the JD text or file under **`data/`** (e.g. `data/acme-backend.md`) or paste it directly.
2. Open **`docs/skills/opportunity-from-jd/SKILL.md`** (or invoke the **opportunity-from-jd** Cursor skill) with your Assistant, including the JD and context from **`data/master.yaml`**.
3. Update **`data/opportunities.yaml`** when you move stages or set next actions (or use **`docs/skills/opportunity-update/SKILL.md`** / skill **opportunity-update**).

---

## Step 4 — Weekly and daily plan

1. **Weekly** — Open **`docs/skills/weekly-planning/SKILL.md`** (or skill **weekly-planning**), set the ISO week and your inputs, run with your Assistant. Save the result as **`data/weekly/<YYYY-Www>.md`** (you can start from `data/weekly/weekly-plan-TEMPLATE.md` or rename/copy it).
2. **Daily** — Use **`data/daily/daily-review-TEMPLATE.md`** as a base for **`data/daily/YYYY-MM-dd-daily-review.md`**, or ask your Assistant to break the current weekly plan into today’s checklist using **`templates/daily_review_template.md`**.

---

## More later

Full details, operating framework, and prompt list live in **[AGENTS.md](AGENTS.md)** (and its chunked framework under `docs/framework/`) and the sections below.

### Where things live

| Need | Location |
|:-----|:---------|
| Profile (fit/gap) | `data/master.yaml` |
| Application pipeline | `data/opportunities.yaml` |
| Working notes | `data/reports/` |
| Optional JD index | `config/jd_catalog.csv` |

Full tree: [docs/REPO_LAYOUT.md](docs/REPO_LAYOUT.md).

### Other opportunity skills

| Goal | Open |
|:-----|:-----|
| Update stage, notes, or close | `docs/skills/opportunity-update/SKILL.md` |
| Full tracking list | `docs/skills/opportunity-report-tracking/SKILL.md` |
| Next steps (one role / rollup) | `docs/skills/opportunity-report-next-steps-one/SKILL.md`, `docs/skills/opportunity-report-next-steps-rollup/SKILL.md` |

Stable links under `prompts/*.md` redirect to the same `SKILL.md` files.

### Data & Git Rules

Everything under **`data/`** stays private (gitignored). Commit framework, docs, and tools normally.

- [docs/BRANCH_WORKFLOW.md](docs/BRANCH_WORKFLOW.md)

### Agent roles

**Copilot** = framework and repo; **Assistant** = analysis and planning runs. [docs/AGENT_ROLES.md](docs/AGENT_ROLES.md).

### Read next

- **[AGENTS.md](AGENTS.md)** — Operating framework index → `docs/framework/{workflows,fit-weights,prompting,cadence}.md`.
- **`data/reports/README.md`** (local vault) — Working notes and reports.
- **[config/context_manifest.yaml](config/context_manifest.yaml)** — Agent context index.
