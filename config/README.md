# Config

- `context_manifest.yaml`: ordered list of files to load for agents (token budgets, visibility). Add entries when you have new **tracked, sanitized** artifacts (includes opportunity templates/prompts; see `docs/cursor/workflows.md` Opportunity Tracking).
- `jd_catalog.csv`: **local only** (gitignored). Copy from `../templates/jd_catalog_template.csv` into this folder and add rows on your machine. Maps `job_id`, alias, role, `raw_path` (local), `normalized_path` (report), `status`. Sanitize before any public export.
- `token_pricing.yaml`: local pricing table for tracked provider/model pairs used by token monitor cost calculation.
- `token_budgets.yaml`: monthly budget thresholds and warning ratio used for alert evaluation.

Do not put PII or raw content in this folder. See `docs/REPO_LAYOUT.md`.
