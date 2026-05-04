#!/usr/bin/env python3
"""
opp.py — single-opportunity accessor/editor for data/private/opportunities.yaml

NOTE: YAML has no random-access format; the full file is always loaded and
rewritten on save. This script keeps the *interface* record-scoped so you
never have to touch the raw YAML manually for common operations.

Usage:
    python scripts/opp.py list [--closed]
    python scripts/opp.py get <id>
    python scripts/opp.py stage <id> <stage>
    python scripts/opp.py next <id> <YYYY-MM-DD> "<action text>"
    python scripts/opp.py close <id> <outcome>
    python scripts/opp.py note <id> "<history line>"
    python scripts/opp.py set <id> <field> <value>
    python scripts/opp.py fields

Stages:   Interested → Applied → RecruiterScreen → HiringManager →
          Technical → OnsiteOrFinal → Offer → Closed
Outcomes: accepted | declined | rejected | withdrawn
"""

import argparse
import os
import sys
import tempfile
from datetime import date
from pathlib import Path
from textwrap import fill, indent

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
DATA_FILE = REPO_ROOT / "data" / "private" / "opportunities.yaml"

# ── Constants ──────────────────────────────────────────────────────────────────

VALID_STAGES = [
    "Interested", "Applied", "RecruiterScreen", "HiringManager",
    "Technical", "OnsiteOrFinal", "Offer", "Closed",
]
VALID_OUTCOMES = {"accepted", "declined", "rejected", "withdrawn"}
VALID_PRIORITIES = {"P0", "P1", "P2"}
HISTORY_MAX = 5

SCALAR_FIELDS = {
    "stage", "stage_entered_at", "next_action", "next_action_date",
    "priority", "notes", "outcome", "closed_at", "updated_at",
    "role_title", "company_display",
}

TODAY = date.today().isoformat()

# ── ANSI colours (skip on Windows without ANSI support) ───────────────────────

_USE_COLOR = sys.stdout.isatty() and os.name != "nt"

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text

def bold(t): return _c("1", t)
def green(t): return _c("32", t)
def yellow(t): return _c("33", t)
def red(t): return _c("31", t)
def dim(t): return _c("2", t)

# ── File I/O ───────────────────────────────────────────────────────────────────

def _load() -> dict:
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with DATA_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print("ERROR: unexpected file format (root must be a mapping).", file=sys.stderr)
        sys.exit(1)
    return data


def _save(data: dict) -> None:
    """Atomic write via temp file to avoid partial writes."""
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=DATA_FILE.parent, prefix=".opp_tmp_", suffix=".yaml"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                width=100,
            )
        os.replace(tmp_path, DATA_FILE)
    except Exception:
        os.unlink(tmp_path)
        raise

# ── Lookup ─────────────────────────────────────────────────────────────────────

def _find(data: dict, opp_id: str) -> tuple[dict, list, int]:
    """
    Return (entry, active_list, index).
    Supports exact match or unambiguous prefix match.
    Exits with error if not found or ambiguous.
    """
    active: list = data.get("active") or []
    exact = [i for i, e in enumerate(active) if e.get("id") == opp_id]
    if exact:
        return active[exact[0]], active, exact[0]

    prefix = [i for i, e in enumerate(active) if str(e.get("id", "")).startswith(opp_id)]
    if len(prefix) == 1:
        i = prefix[0]
        print(dim(f"  (matched prefix → {active[i]['id']})"))
        return active[i], active, i
    if len(prefix) > 1:
        matches = ", ".join(active[i]["id"] for i in prefix)
        print(f"ERROR: ambiguous id prefix '{opp_id}' matches: {matches}", file=sys.stderr)
        sys.exit(1)

    print(f"ERROR: no opportunity with id '{opp_id}'.", file=sys.stderr)
    sys.exit(1)

# ── Display helpers ────────────────────────────────────────────────────────────

def _priority_color(p: str) -> str:
    return {"P0": red, "P1": yellow, "P2": dim}.get(p, str)(p)


def _stage_color(s: str) -> str:
    closed_color = dim if s == "Closed" else str
    return {"Offer": green, "Closed": dim}.get(s, str)(s)


def _fmt_entry(e: dict) -> str:
    lines = []
    lines.append(bold(f"{e.get('company_display', '?')} — {e.get('role_title', '?')}"))
    lines.append(
        f"  id       : {e.get('id', '?')}"
        f"   stage    : {_stage_color(e.get('stage', '?'))}"
        f"   priority : {_priority_color(e.get('priority', '?'))}"
    )
    if e.get("stage_entered_at"):
        lines.append(f"  entered  : {e['stage_entered_at']}")
    if e.get("next_action_date"):
        past = e["next_action_date"] < TODAY
        date_str = red(e["next_action_date"]) if past else e["next_action_date"]
        lines.append(f"  next date: {date_str}")
    if e.get("next_action"):
        wrapped = fill(e["next_action"], width=90)
        lines.append(f"  next     : {wrapped}")
    if e.get("notes"):
        wrapped = fill(e["notes"], width=88)
        lines.append(f"  notes    :\n{indent(wrapped, '    ')}")
    if e.get("outcome"):
        lines.append(f"  outcome  : {e['outcome']}   closed: {e.get('closed_at', '?')}")
    if e.get("contacts"):
        lines.append("  contacts :")
        for c in e["contacts"]:
            ch = c.get("channels") or {}
            ch_str = "  ".join(f"{k}: {v}" for k, v in ch.items()) if ch else ""
            lines.append(f"    • {c.get('name', '?')} ({c.get('role', '?')})  {ch_str}")
            if c.get("notes"):
                lines.append(f"      {dim(c['notes'])}")
    if e.get("links"):
        lines.append("  links    :")
        for k, v in e["links"].items():
            lines.append(f"    {k}: {v}")
    if e.get("history"):
        lines.append("  history  :")
        for h in e["history"]:
            lines.append(f"    {dim('·')} {h}")
    lines.append(f"  updated  : {e.get('updated_at', '?')}")
    return "\n".join(lines)

# ── Commands ───────────────────────────────────────────────────────────────────

def cmd_list(args: argparse.Namespace) -> None:
    data = _load()
    active: list = data.get("active") or []
    show_closed = args.closed

    rows = []
    for e in active:
        stage = e.get("stage", "?")
        if stage == "Closed" and not show_closed:
            continue
        ndate = e.get("next_action_date", "")
        past = ndate and ndate < TODAY
        date_disp = (red(ndate) if past else ndate) if ndate else dim("—")
        rows.append((
            _priority_color(e.get("priority", "?")),
            _stage_color(stage),
            date_disp,
            e.get("id", "?"),
            e.get("company_display", "?"),
        ))

    if not rows:
        print(dim("No active opportunities."))
        return

    print(f"\n{'PRI':<4} {'STAGE':<18} {'NEXT DATE':<12} {'ID':<44} COMPANY")
    print("─" * 110)
    for pri, stage, ndate, oid, company in rows:
        # strip ANSI for width calculation
        raw_stage = stage.replace("\033[0m", "").replace("\033[2m", "").replace("\033[32m", "").replace("\033[33m", "").replace("\033[31m", "")
        raw_date = ndate.replace("\033[0m", "").replace("\033[31m", "").replace("\033[2m", "")
        raw_pri = pri.replace("\033[0m", "").replace("\033[31m", "").replace("\033[33m", "").replace("\033[2m", "")
        pad_stage = stage + " " * max(0, 18 - len(raw_stage))
        pad_date = ndate + " " * max(0, 12 - len(raw_date))
        pad_pri = pri + " " * max(0, 4 - len(raw_pri))
        print(f"{pad_pri} {pad_stage} {pad_date} {oid:<44} {company}")
    print()


def cmd_get(args: argparse.Namespace) -> None:
    data = _load()
    entry, _, _ = _find(data, args.id)
    print()
    print(_fmt_entry(entry))
    print()


def cmd_stage(args: argparse.Namespace) -> None:
    stage = args.stage
    if stage not in VALID_STAGES:
        print(f"ERROR: invalid stage '{stage}'. Valid: {', '.join(VALID_STAGES)}", file=sys.stderr)
        sys.exit(1)

    data = _load()
    entry, active, idx = _find(data, args.id)
    old_stage = entry.get("stage", "?")

    entry["stage"] = stage
    entry["stage_entered_at"] = TODAY
    entry["updated_at"] = TODAY

    if stage == "Closed":
        if not args.outcome:
            print("ERROR: closing an opportunity requires --outcome (accepted|declined|rejected|withdrawn)", file=sys.stderr)
            sys.exit(1)
        outcome = args.outcome
        if outcome not in VALID_OUTCOMES:
            print(f"ERROR: invalid outcome '{outcome}'.", file=sys.stderr)
            sys.exit(1)
        entry["outcome"] = outcome
        entry["closed_at"] = TODAY

    _append_history(entry, f"{TODAY}: Stage {old_stage} → {stage}.")
    active[idx] = entry
    data["active"] = active
    _save(data)
    print(green(f"✓ {entry['id']}: stage {old_stage} → {stage}  (entered {TODAY})"))


def cmd_next(args: argparse.Namespace) -> None:
    data = _load()
    entry, active, idx = _find(data, args.id)

    entry["next_action_date"] = args.date
    entry["next_action"] = args.action
    entry["updated_at"] = TODAY

    active[idx] = entry
    data["active"] = active
    _save(data)
    print(green(f"✓ {entry['id']}: next action set → {args.date}"))
    print(f"  {args.action}")


def cmd_close(args: argparse.Namespace) -> None:
    outcome = args.outcome
    if outcome not in VALID_OUTCOMES:
        print(f"ERROR: invalid outcome '{outcome}'. Valid: {', '.join(sorted(VALID_OUTCOMES))}", file=sys.stderr)
        sys.exit(1)

    data = _load()
    entry, active, idx = _find(data, args.id)

    old_stage = entry.get("stage", "?")
    entry["stage"] = "Closed"
    entry["stage_entered_at"] = TODAY
    entry["outcome"] = outcome
    entry["closed_at"] = TODAY
    entry["updated_at"] = TODAY

    note = f"{TODAY}: Closed — {outcome}."
    if args.note:
        note += f" {args.note}"
    _append_history(entry, note)

    active[idx] = entry
    data["active"] = active
    _save(data)
    print(green(f"✓ {entry['id']}: closed ({outcome})  was: {old_stage}"))


def cmd_note(args: argparse.Namespace) -> None:
    data = _load()
    entry, active, idx = _find(data, args.id)

    line = args.note
    if not line.startswith(TODAY):
        line = f"{TODAY}: {line}"
    _append_history(entry, line)
    entry["updated_at"] = TODAY

    active[idx] = entry
    data["active"] = active
    _save(data)
    print(green(f"✓ {entry['id']}: history note appended."))
    print(f"  {dim(line)}")


def cmd_set(args: argparse.Namespace) -> None:
    field = args.field
    if field not in SCALAR_FIELDS:
        print(
            f"ERROR: '{field}' is not a settable scalar field.\n"
            f"Use 'python scripts/opp.py fields' to list them.",
            file=sys.stderr,
        )
        sys.exit(1)

    data = _load()
    entry, active, idx = _find(data, args.id)
    old = entry.get(field, dim("<unset>"))
    entry[field] = args.value
    entry["updated_at"] = TODAY

    active[idx] = entry
    data["active"] = active
    _save(data)
    print(green(f"✓ {entry['id']}: {field}"))
    print(f"  {dim(str(old))} → {args.value}")


def cmd_fields(_args: argparse.Namespace) -> None:
    print("\nSettable scalar fields (via 'set' command):")
    for f in sorted(SCALAR_FIELDS):
        print(f"  {f}")
    print("\nFor contacts/links, edit the YAML directly or extend this script.")
    print()

# ── History helper ─────────────────────────────────────────────────────────────

def _append_history(entry: dict, line: str) -> None:
    history: list = entry.get("history") or []
    history.append(line)
    if len(history) > HISTORY_MAX:
        history = history[-HISTORY_MAX:]
    entry["history"] = history

# ── CLI ────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="opp",
        description="Single-opportunity accessor/editor for opportunities.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # list
    sp = sub.add_parser("list", help="List active opportunities (table)")
    sp.add_argument("--closed", action="store_true", help="Include closed entries")
    sp.set_defaults(func=cmd_list)

    # get
    sp = sub.add_parser("get", help="Print a single opportunity")
    sp.add_argument("id", help="Opportunity id (or unambiguous prefix)")
    sp.set_defaults(func=cmd_get)

    # stage
    sp = sub.add_parser("stage", help="Update stage")
    sp.add_argument("id", help="Opportunity id (or prefix)")
    sp.add_argument("stage", choices=VALID_STAGES, metavar="stage")
    sp.add_argument("--outcome", help="Required when stage=Closed")
    sp.set_defaults(func=cmd_stage)

    # next
    sp = sub.add_parser("next", help="Set next_action and next_action_date")
    sp.add_argument("id", help="Opportunity id (or prefix)")
    sp.add_argument("date", help="YYYY-MM-DD")
    sp.add_argument("action", help="Action description (quote it)")
    sp.set_defaults(func=cmd_next)

    # close
    sp = sub.add_parser("close", help="Close an opportunity with outcome")
    sp.add_argument("id", help="Opportunity id (or prefix)")
    sp.add_argument("outcome", choices=sorted(VALID_OUTCOMES), metavar="outcome")
    sp.add_argument("--note", help="Optional closing note for history")
    sp.set_defaults(func=cmd_close)

    # note
    sp = sub.add_parser("note", help="Append a line to history[]")
    sp.add_argument("id", help="Opportunity id (or prefix)")
    sp.add_argument("note", help="History note (today's date prepended automatically)")
    sp.set_defaults(func=cmd_note)

    # set
    sp = sub.add_parser("set", help="Set any scalar field")
    sp.add_argument("id", help="Opportunity id (or prefix)")
    sp.add_argument("field", help="Field name (run 'fields' to list)")
    sp.add_argument("value", help="New value (string)")
    sp.set_defaults(func=cmd_set)

    # fields
    sp = sub.add_parser("fields", help="List settable scalar fields")
    sp.set_defaults(func=cmd_fields)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
