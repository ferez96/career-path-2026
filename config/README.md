# Config

- `context_manifest.yaml`: three-section agent context index:
  - `groups:` — named clusters of context IDs (e.g. `always-required`, `weekly-planning`, `fit-scoring`, `company-brief`, `opportunity-core`, `opportunity-reports`, `governance`).
  - `triggers:` — map skill/task name → groups to load; agents pick the matching trigger and load only those groups.
  - `contexts:` — individual file entries with path, token_budget, and visibility. Add entries here when you have new **tracked, sanitized** artifacts, then reference the new id in the appropriate group (see `docs/framework/workflows.md` Opportunity Tracking for pipeline context).
- `jd_catalog.csv`: **local only** (gitignored). Copy from `../templates/jd_catalog_template.csv` into this folder and add rows on your machine. Maps `job_id`, alias, role, `raw_path` (local), `normalized_path` (report), `status`. Sanitize before any public export.
- `token_pricing.yaml`: local pricing table for tracked provider/model pairs used by token monitor cost calculation.
- `token_budgets.yaml`: monthly budget thresholds and warning ratio used for alert evaluation.

Do not put PII or raw content in this folder. See `docs/REPO_LAYOUT.md`.
