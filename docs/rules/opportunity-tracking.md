
# Opportunity tracking

- **Canonical source:** `data/private/opportunities.yaml` (gitignored). Schema: `templates/opportunities_tracker_template.yaml`.
- **Raw JDs:** `data/raw/` (`raw-ingest`). Optional: row in `config/jd_catalog.csv`.
- **Full reports (company names, detail):** `data/reports/pipeline/`, `data/reports/roles/`, etc. (see `data/VAULT_LAYOUT.md`) or chat only — class `private-sensitive` (no in-vault sanitization required).
- **Publishing outside `data/`:** aliases or scrubbed descriptions only. Do not invent JD text or pipeline state.
- **Skills:** `docs/skills/opportunity*/SKILL.md` (stable links: `prompts/opportunity-*.md`) — always include **Assumptions** / **Risk** when generating reports (per `docs/framework/prompting.md`).

## Preferred write tool — `scripts/opp.py`

For any write to a **single existing** opportunity, use `python scripts/opp.py` instead of editing the YAML directly.

**Full reference:** `docs/opp-cli.md`
