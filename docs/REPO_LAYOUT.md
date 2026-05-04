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
├── scripts/                # bootstrap.ps1 / bootstrap.sh
├── apps/                   # Runtime entry points (web, cli)
├── core/                   # Business logic (cost, index/tasks/prompts interfaces)
├── adapters/               # Provider, storage, and telemetry integrations
├── prompts/                # Redirect stubs → `docs/skills/*/SKILL.md`
├── docs/
│   ├── framework/          # Shared framework docs (workflows, fit-weights, prompting, cadence)
│   ├── skills/             # Canonical skill definitions (tool-agnostic SKILL.md files)
│   ├── rules/              # Canonical rule content (tool-agnostic plain markdown)
│   └── *.md                # Policy, classification, layout docs
├── reports/
│   ├── benchmarks/         # Benchmark / JD analysis (derived-sanitized)
│   ├── briefs/             # Company / org brief (derived-sanitized)
│   └── private/            # Private reports — gitignored
├── templates/              # Markdown + YAML templates (e.g. opportunity tracker schema)
├── .cursor/rules/          # Cursor adapters — frontmatter only; canonical content in docs/rules/
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
| Assistant workflows (Cursor Skills) | `docs/skills/*/SKILL.md` |
| Stable links / redirects | `prompts/*.md` (point to skills) |
| Sanitized reports (public-safe) | `reports/benchmarks/`, `reports/briefs/` |
| Private opportunity reports (full detail) | `reports/private/` (gitignored) |
| Opportunity tracker (schema template) | `templates/opportunities_tracker_template.yaml` → copy to `data/private/opportunities.yaml` |
| Opportunity workflows | `docs/skills/opportunity-*/SKILL.md` (see `prompts/opportunity-*.md` redirects) |
| Context index + job mapping | `config/context_manifest.yaml`, `config/jd_catalog.csv` |
| Token pricing / budget configs | `config/token_pricing.yaml`, `config/token_budgets.yaml` |
| Token monitor runtime | `apps/web/`, `apps/cli/`, `core/cost/`, `adapters/{llm,telemetry,storage/sqlite}` |
| Token usage local DB | `data/private/token_usage.db` (local, gitignored) |


## When unsure

Mark **`NEEDS_REVIEW`** in the PR/commit and follow `docs/DATA_CLASSIFICATION.md`.
