---
name: opportunity-update
description: >-
  Updates one opportunity in opportunities.yaml (stage, next actions, close
  outcome, history). Use when the user changes pipeline stage, notes, next_action,
  or closes an opportunity by id.
---

# Update an opportunity (status / content)

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- Current tracker: `data/private/opportunities.yaml` (private) — read for full context, but prefer `opp.py` for writes
- Schema reference: `templates/opportunities_tracker_template.yaml`
- CLI reference: `docs/opp-cli.md`

**Task:**
1. Identify the record by **`id`** (or company + role — resolve to id first).
2. Apply updates using `python scripts/opp.py` for all scalar field changes. See `docs/opp-cli.md` for the full command reference.
3. **Edit YAML directly only for:**
   - **`contacts[]`** — add/update/remove a contact entry (`name`, `role`, `channels` map, `notes`). Merge with existing list; do not wipe entries not mentioned.
   - **`links`** — add or update a URL key (`application_portal`, `job_posting`, or free key). Merge with existing keys.
4. Confirm the result with `python scripts/opp.py get <id>` after any write.

**Output:**
- The `opp.py` command(s) run and their output
- If any YAML edit was needed (contacts/links): show the patch applied
- If stage transition is unusual, one-line **sanity check** (e.g. Offer without Technical — flag for user)
- **Assumptions** / **Risk**

**Constraints:**
- Do not remove unrelated opportunities.
- No PII in public-bound outputs.
- **Do not fabricate.** Only apply changes explicitly stated by the user. Do not infer, fill in, or default unmentioned fields.
- Every inference (e.g. resolving id from company name, assuming stage_entered_at = today) must be listed in **Assumptions** and confirmed before applying the patch.

**My inputs (collect, confirm, or ask):**
- If **opportunity id** or **intended changes** are **not** clear from memory, chat, or `data/private/opportunities.yaml`: **ask** before proposing the patch.
- If you resolve **id** from company + role or infer updates from context: state your resolution and **ask the user to confirm or correct** before final output.
- Opportunity id: `<...>`
- Changes: `<...>`
