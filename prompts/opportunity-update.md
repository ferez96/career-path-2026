# Prompt: update an opportunity (status / content) (reuse)

Copy into a new chat. Replace bracketed fields.

---

**Role:** Assistant — career / opportunity tracking (see `docs/AGENT_ROLES.md`).

**Context to load:**
- Current tracker: `data/private/opportunities.yaml` (private)
- Schema reference: `templates/opportunities_tracker_template.yaml`

**Task:**
1. Identify the record by **`id`**: `<OPPORTUNITY_ID>` (or company + role if user specifies).
2. Apply updates:
   - **`stage`** (must be one of the allowed pipeline stages) and optionally **`stage_entered_at`**
   - **`next_action`**, **`next_action_date`**, **`priority`**, **`notes`**
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

---

**My inputs (fill in):**
- Opportunity id: `<...>`
- Changes: `<...>`

---
