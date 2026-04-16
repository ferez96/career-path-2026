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
│   ├── raw/                # Raw JD/benchmark — gitignored (only .keep in repo)
│   └── private/            # Resume, master.yaml — gitignored
├── docs/                   # Policy, workflow, classification
├── prompts/                # Assistant prompts
├── reports/
│   ├── benchmarks/         # Benchmark / JD analysis (derived-sanitized)
│   ├── briefs/             # Company / org brief (derived-sanitized)
│   └── private/            # Private reports — gitignored
├── templates/              # Markdown templates
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
| Prompts for the AI | `prompts/` |
| Sanitized reports (public-safe) | `reports/benchmarks/`, `reports/briefs/` |
| Context index + job mapping | `config/context_manifest.yaml`, `config/jd_catalog.csv` |


## When unsure

Mark **`NEEDS_REVIEW`** in the PR/commit and follow `docs/DATA_CLASSIFICATION.md`.
