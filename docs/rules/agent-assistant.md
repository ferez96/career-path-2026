
# Assistant — operations & analysis

- Read `docs/AGENT_ROLES.md` (Assistant). For workflows see `docs/framework/workflows.md`; for KPIs/cadence see `docs/framework/cadence.md`; for prompting rules see `docs/framework/prompting.md`.
- **Obsidian-first routing:** vault root is `data/`. For JD ingest, opportunity Q&A, or pipeline reports, start from `data/atlas/Navigation — JD and Opportunities.md` (or the relevant `* Opportunity Index.md`) and read only linked leaves—avoid whole-folder reads and raw exports unless the task requires them.
- Analysis / fit / gap: follow `docs/rules/career-path-resume.md` (resume via `data/master.yaml` when applicable). **`data/**` is a private vault** — full detail is fine there. **Public-bound** output (tracked paths outside `data/` on `master`) must stay non-PII.
- Prefer context in `config/context_manifest.yaml`; use `config/jd_catalog.csv` to trace benchmarks.
- Missing data → `Unknown`; include **Assumptions** and **Risk** when the framework requires them.
