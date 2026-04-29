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
6. If the user supplies any contact info (recruiter, HM, referral), populate **`contacts[]`** — each item: `name`, `role` (`recruiter|hiring_manager|referral|hr|other`), `channels` (free map: any platform key → handle/URL/number, e.g. `linkedin`, `email`, `zalo`, `whatsapp`, `telegram`, `messenger`, `phone`), and `notes`. Omit the key entirely if no contacts are known.
7. If the JD or user provides a portal or posting URL, populate **`links`** (`application_portal`, `job_posting`, or a free key). These are the canonical spots for manual status checks. Omit the key if no URLs are known.
8. Set **`updated_at`** to today (ISO date).
9. Output a **YAML snippet** ready to append under `active:` in `data/private/opportunities.yaml` (or merge instructions if file already exists). Do not duplicate `id`.

**Output sections:**
- YAML block for the new `active[]` item only
- If jd_catalog row suggested: CSV line or table row
- **Assumptions** / **Risk**

**Constraints:**
- No PII in any content intended for public `reports/` or `reports/briefs/`.
- **Do not fabricate.** Only use values explicitly present in the JD file or stated by the user. Do not invent role details, company facts, contact info, or URLs.
- If a field cannot be extracted from the JD or user input: use `Unknown` as a placeholder, note it in **Assumptions**, and ask one clarifying question before locking `id` or `company_display`.
- Every inference (e.g. stage guessed from tone, priority guessed from urgency language) must be listed in **Assumptions** and confirmed by the user before final output.

**My inputs (collect, confirm, or ask):**
- If any item below is **not** already known from memory, prior messages, or repo (`data/raw/`, `opportunities.yaml`): **ask** before emitting final YAML.
- If you **infer** an item (e.g. stage from user tone, path from last-opened file): state it briefly and **ask the user to confirm or correct** before final output.
- Path to JD under `data/raw/`: `<...>`
- Desired initial stage: `<Interested | Applied | ...>`
- job_id for catalog (or "skip catalog"): `<...>`
- Contacts (recruiter / HM / referral name + role + linkedin/email if known, or "none"): `<...>`
- Application portal / job posting URL (or "none"): `<...>`
