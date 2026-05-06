# opp.py — opportunity CLI reference

Single-opportunity accessor/editor for `data/private/opportunities.yaml`.

**Why use this instead of editing YAML directly:** auto-manages `updated_at`,
`stage_entered_at`, history capping (max 5 entries), and atomic writes.

## Commands

| Operation | Command |
|:----------|:--------|
| List pipeline | `python scripts/opp.py list` |
| Inspect one record | `python scripts/opp.py get <id>` |
| Advance stage | `python scripts/opp.py stage <id> <stage>` |
| Update next action | `python scripts/opp.py next <id> <YYYY-MM-DD> "<action>"` |
| Close | `python scripts/opp.py close <id> <outcome> [--note "..."]` |
| Append history note | `python scripts/opp.py note <id> "<note>"` |
| Set scalar field | `python scripts/opp.py set <id> <field> <value>` |
| List settable fields | `python scripts/opp.py fields` |

Stages: `Interested → Applied → RecruiterScreen → HiringManager → Technical → OnsiteOrFinal → Offer → Closed`
Outcomes: `accepted | declined | rejected | withdrawn`

## Id matching

Accepts exact id or unambiguous prefix: `shopback` → `shopback-staff-senior-backend-2026`.

## Exceptions — edit YAML directly

- **New opportunities** — `opp.py` has no `add` command; use the `opportunity-from-jd` skill.
- **`contacts[]`** and **`links`** — nested structures; not supported by `opp.py`.

## Tests

```
python scripts/test_opp.py -v
```
