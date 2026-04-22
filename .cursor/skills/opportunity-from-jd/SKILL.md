---
name: opportunity-from-jd
description: >-
  Reads a raw JD and produces a YAML snippet for opportunities.yaml plus optional
  jd_catalog.csv row. Use when adding a new pipeline opportunity from data/raw,
  ingesting a JD file, or bootstrapping opportunity id and next_action fields.
---

# Add opportunity from a JD file

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- Raw JD file: `data/raw/<FILENAME>` (local; `raw-ingest`, do not paste full JD into public `reports/`)
- Schema: `templates/opportunities_tracker_template.yaml`
- Optional: `data/private/master.yaml` for a one-line fit note (private)
- Optional: `config/jd_catalog.csv` to register `job_id`

**Task:**
1. Read the JD. Extract **role_title**, a **company_display** string (as written in JD or user label), location/work mode if relevant for notes.
2. Propose **`id`**: short slug, unique in `data/private/opportunities.yaml` (e.g. `acme-senior-backend-2026`).
3. Set initial **`stage`**: usually `Interested` or `Applied` (user may override).
4. Set **`jd_source`**: at minimum `raw_path: "data/raw/<FILENAME>"`. If user wants catalog tracking, output one CSV row for `jd_catalog.csv` with columns `job_id,alias,role,raw_path,normalized_path,status` (fill unknowns with placeholder or ask).
5. Set **`next_action`** and **`next_action_date`** (concrete, within 7 days if possible), **`priority`** (P0/P1/P2), short **`notes`**.
6. Set **`updated_today`** in **`updated_at`** (ISO date).
7. Output a **YAML snippet** ready to append under `active:` in `data/private/opportunities.yaml` (or merge instructions if file already exists). Do not duplicate `id`.

**Output sections:**
- YAML block for the new `active[]` item only
- If jd_catalog row suggested: CSV line or table row
- **Assumptions** / **Risk**

**Constraints:**
- No PII in any content intended for public `reports/` or `reports/briefs/`.
- If data missing, use `Unknown` and ask one clarifying question before locking `id` or `company_display`.

**My inputs (collect, confirm, or ask):**
- If any item below is **not** already known from memory, prior messages, or repo (`data/raw/`, `opportunities.yaml`): **ask** before emitting final YAML.
- If you **infer** an item (e.g. stage from user tone, path from last-opened file): state it briefly and **ask the user to confirm or correct** before final output.
- Path to JD under `data/raw/`: `<...>`
- Desired initial stage: `<Interested | Applied | ...>`
- job_id for catalog (or "skip catalog"): `<...>`
