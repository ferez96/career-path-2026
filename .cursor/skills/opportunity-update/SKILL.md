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
- Current tracker: `data/private/opportunities.yaml` (private)
- Schema reference: `templates/opportunities_tracker_template.yaml`

**Task:**
1. Identify the record by **`id`**: `<OPPORTUNITY_ID>` (or company + role if user specifies).
2. Apply updates:
   - **`stage`** (must be one of the allowed pipeline stages); when stage changes, set **`stage_entered_at`** to today unless the user specifies a different date
   - **`next_action`**, **`next_action_date`**, **`priority`**, **`notes`**
   - **`contacts[]`** — add, update, or remove a contact entry (`name`, `role`, `channels` free map of platform → handle/URL/number, `notes`). Merge with existing list; do not wipe entries not mentioned.
   - **`links`** — add or update a URL key (`application_portal`, `job_posting`, or free key). Merge with existing keys.
   - If moving to **Closed**: set **`outcome`** (`accepted` | `declined` | `rejected` | `withdrawn`), **`closed_at`** (ISO date)
3. Set **`updated_at`** to today (ISO date).
4. Optionally append **one line** to **`history`** (short audit, max ~5 recent lines; drop oldest if needed).

**Output:**
- A **minimal YAML patch** description: which fields change, or a full replacement block for that list item
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
