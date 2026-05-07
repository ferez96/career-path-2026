# JD Full Workflow Guide

Step-by-step reference for the `/jd-process` skill — from raw JD drop to opportunity import.

---

## Overview

**One entry point, full pipeline:** drop a raw JD file and invoke `/jd-process` to get normalized JD, company research, fit/gap analysis, decision brief, and a ready-to-import opportunity entry — all in one pass.

```
data/raw/{jd.txt}
  ↓  normalize
data/jds/{slug}.md
  ↓  research + score
data/reports/roles/{slug}-analysis.md
data/reports/roles/{slug}-company-brief.md
data/reports/roles/{slug}-decision.md
  ↓  import
opportunities.yaml  ← YAML snippet (confirm + insert)
config/jd_catalog.csv  ← CSV row (confirm + insert)
```

---

## Step 1 — Drop the raw JD

Copy or save the JD file (any format: `.txt`, `.md`, `.pdf` extract) into:

```
data/raw/{descriptive-filename}
```

**Naming convention:** `{company}-{role-short}-{YYYY-MM}.txt`
Example: `acme-senior-backend-2026-04.txt`

> `data/raw/` is `raw-ingest` class — gitignored, never committed.

---

## Step 2 — Invoke the skill

Start a conversation with the Assistant agent and invoke:

```
/jd-process
- File: data/raw/acme-senior-backend-2026-04.txt
- Company: Acme Corp
```

**Required inputs:**
| Input | Example | Notes |
|---|---|---|
| `File` | `data/raw/acme-senior-backend-2026-04.txt` | Must exist in `data/raw/` |
| `Company` | `Acme Corp` | Full name; used for research + slug disambiguation |

**Optional inputs:**
| Input | Default | Notes |
|---|---|---|
| `Stage` | `Interested` | Use `Applied` if already submitted |
| `Priority` | `P1` | Override with `P0` or `P2` if known |

---

## Step 3 — Use Obsidian to keep context small

Before reading large files, route through the vault hubs:

1. Open `data/atlas/Navigation — JD and Opportunities.md`.
2. For a new JD, follow **G1**: Ingest → raw source → normalized `data/jds/{slug}.md`.
3. For an existing opportunity, follow **G3**: `data/opportunities/Central Opportunities.md` → `{Company} Opportunity Index` → linked JD/reports.

Useful CLI commands:

```powershell
obsidian read vault=data "path=atlas/Navigation — JD and Opportunities.md"
obsidian read vault=data "path=opportunities/Stripe Opportunity Index.md"
obsidian links vault=data "path=opportunities/Stripe Opportunity Index.md"
python scripts/vault_hub_wikilinks.py
```

Prefer normalized JDs and linked role reports before raw PDFs, `.mhtml` files, or broad folder reads.

---

## Step 4 — Confirm the slug

The skill proposes a unique ID (slug) before proceeding:
```
Proposed slug: acme-senior-backend-2026-04
Check jd_catalog.csv: no conflict found.
Confirm? (or provide alternative)
```

Confirm or provide a different slug. The slug becomes:
- The opportunity ID in `opportunities.yaml`
- The filename base for all reports and the normalized JD

---

## Step 5 — Review the pipeline output

The skill runs all sub-workflows automatically:

| Step | What happens |
|---|---|
| **Normalize** | Extracts role, company, level, skills, responsibilities → `data/jds/{slug}.md` |
| **Research** | Runs `company-brief` skill → company tier, size, product, culture, risks |
| **Score** | Applies `fit-weights.md` rubric against `master.yaml` profile |
| **Reports** | Generates 3 markdown files in `data/reports/roles/` |
| **Import** | Proposes YAML snippet + catalog CSV row |

This takes a few minutes for the research step (web search involved).

---

## Step 6 — Review reports

Check the three private reports:

| File | Contents |
|---|---|
| `data/reports/roles/{slug}-analysis.md` | Fit scoring table, gaps, 48h action plan |
| `data/reports/roles/{slug}-company-brief.md` | Company research (tier, culture, DX, risks) |
| `data/reports/roles/{slug}-decision.md` | 1-page executive summary + recommendation |

> Reports are `private-sensitive` — gitignored, local only. Do not commit raw.

---

## Step 7 — Confirm and insert YAML

The skill outputs a YAML snippet. Review and insert it into `data/private/opportunities.yaml` under `active:`:

```yaml
active:
  - id: acme-senior-backend-2026-04
    company_display: "Acme Corp"
    role_title: "Senior Backend Engineer"
    stage: Interested
    priority: P1
    next_action: "Review JD analysis and schedule time to apply"
    next_action_date: "2026-04-30"
    notes: "Fit score: 78/100. Strong backend match, gap in domain X."
    jd_source:
      raw_path: "data/raw/acme-senior-backend-2026-04.txt"
    updated_at: "2026-04-28"
    history: []
```

Adjust `stage`, `priority`, `next_action`, and `next_action_date` to reflect your actual situation.

---

## Step 8 — Confirm and insert catalog row

The skill outputs a CSV row. Insert it into `config/jd_catalog.csv`:

```
acme-senior-backend-2026-04,acme-senior-backend-2026-04,Senior Backend Engineer,Acme Corp,data/raw/acme-senior-backend-2026-04.txt,data/jds/acme-senior-backend-2026-04.md,new,2026-04-28
```

> `config/jd_catalog.csv` is gitignored (created from the template). Keep it local.

---

## Step 9 — (Optional) Publish an excerpt to the public repo

The vault under `data/` stays private — **no checklist required** for files that remain there.

If you want a **tracked, public** artifact on `master`:

1. Run `docs/SANITIZATION_CHECKLIST.md` on the text you will commit
2. Remove or redact: company name, salary, specific contacts, identifying details
3. Add the redacted version under a **public-bound path** (e.g. a new `docs/` example or anonymized appendix — not necessarily under `data/`)
4. Commit to `master` branch

---

## Data Classification Reference

| Path | Class | Git |
|---|---|---|
| `data/raw/*` | `raw-ingest` | Ignored |
| `data/**` (incl. `jds/`, `reports/**`, etc.) | `private-sensitive` | Ignored — local vault; no in-place sanitization required |
| `config/jd_catalog.csv` | `derived-sanitized` if committed | Often ignored locally |

---

## Troubleshooting

**"File not found in data/raw/"**
→ Confirm the file is in the right directory and the filename matches exactly.

**"Slug conflict with existing entry"**
→ The skill will suggest a variant (e.g., add `-2` suffix). Confirm or provide your own.

**"Company research is incomplete / Unknown"**
→ Expected for lesser-known companies. Review the brief and add context manually if needed.

**Company name is ambiguous (e.g., "Atlas")**
→ Provide disambiguation in the Company input: `Company: Atlas (logistics platform, Singapore)`.

---

## Related Skills

| Skill | When to use |
|---|---|
| `/company-brief` | Standalone company research, without JD |
| `/opportunity-from-jd` | Add to tracker only, without full analysis |
| `/opportunity-update` | Update stage/action after jd-process |
| `/opportunity-report-tracking` | Review full pipeline status |
