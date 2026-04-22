# Repository layout (canonical)

Goals: **fewer top-level folders**, **one place for raw input**, **one place for sanitized output**, **config separated from content**.

## Directory tree (summary)

```text
.
├── config/                 # Agent index + catalog (no PII)
├── data/
│   ├── career_path_master.csv
│   ├── daily/              # Daily reviews and logs
│   ├── weekly/             # Weekly tracking (anonymize before public)
│   ├── raw/                # Raw JD/benchmark — contents gitignored
│   └── private/            # Canonical profile (master.yaml), opportunities.yaml, CV — gitignored
├── docs/                   # Policy, workflow, classification
├── scripts/                # bootstrap.ps1 / bootstrap.sh
├── prompts/                # Redirect stubs → `.cursor/skills/*/SKILL.md`
├── .cursor/skills/         # Canonical Assistant workflows (Cursor Skills)
├── reports/
│   ├── benchmarks/         # Benchmark / JD analysis (derived-sanitized)
│   ├── briefs/             # Company / org brief (derived-sanitized)
│   └── private/            # Private reports — gitignored
├── templates/              # Markdown + YAML templates (e.g. opportunity tracker schema)
├── .cursor/rules/          # Cursor rules (Copilot vs Assistant)
├── CURSOR.md
└── README.md
```

## Where to put files

| Need | Location |
|:-----|:---------|
| Raw JD/benchmark, PDF, unprocessed paste | `data/raw/` (local, gitignored) |
| Career milestones, CSV tracking | `data/career_path_master.csv` |
| Daily review / journal | `data/daily/` |
| Weekly plan / review | `data/weekly/` |
| Assistant workflows (Cursor Skills) | `.cursor/skills/*/SKILL.md` |
| Stable links / redirects | `prompts/*.md` (point to skills) |
| Sanitized reports (public-safe) | `reports/benchmarks/`, `reports/briefs/` |
| Private opportunity reports (full detail) | `reports/private/` (gitignored) |
| Opportunity tracker (schema template) | `templates/opportunities_tracker_template.yaml` → copy to `data/private/opportunities.yaml` |
| Opportunity workflows | `.cursor/skills/opportunity-*/SKILL.md` (see `prompts/opportunity-*.md` redirects) |
| Context index + job mapping | `config/context_manifest.yaml`, `config/jd_catalog.csv` |


## When unsure

Mark **`NEEDS_REVIEW`** in the PR/commit and follow `docs/DATA_CLASSIFICATION.md`.
