# Config

- `context_manifest.yaml`: ordered list of files to load for agents (token budgets, visibility). Add entries when you have new **tracked, sanitized** artifacts.
- `jd_catalog.csv`: maps `job_id`, alias, role, `raw_path` (local), `normalized_path` (report). Ships with **headers only**; add rows locally or on `personal`, then sanitize before public.

Do not put PII or raw content in this folder. See `docs/REPO_LAYOUT.md`.
