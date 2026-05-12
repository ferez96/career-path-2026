# opp.py — opportunity CLI

Single-opportunity accessor/editor for `data/opportunities.yaml`.

**Command reference:** run from the repo root:

```text
python scripts/opp.py --help
python scripts/opp.py <command> --help
```

That output is the canonical list of subcommands, flags, arguments, and **agent guidance** (what to do outside this CLI). It lives in `scripts/opp.py` so it cannot drift from the implementation.

**Why use this instead of editing YAML directly:** the script manages `updated_at`, `stage_entered_at`, caps `history` (max 5 entries), and writes atomically.

## Tests

```text
python scripts/test_opp.py -v
```
