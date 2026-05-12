# Quick start

---

## Step 1 — Install

From the **root of the repository**, create a local **`data/`** tree as needed.

Templates and default install paths:

| Template                                   | Installed path                          |
|:--------------------------------------------|:----------------------------------------|
| `templates/opportunities_tracker_template.yaml` | `data/opportunities.yaml`               |
| `templates/master_template.yaml`                | `data/master.yaml`                      |
| `templates/jd_catalog_template.csv`             | `data/jd_catalog.csv`                 |

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

## More later

Full details and operating framework live in **[AGENTS.md](AGENTS.md)**. You can ask your AI agent to help you explore.

