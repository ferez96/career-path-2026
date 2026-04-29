#!/usr/bin/env python3
"""Validate data/private/opportunities.yaml against the opportunity schema."""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
DATA_FILE = REPO_ROOT / "data" / "private" / "opportunities.yaml"

VALID_STAGES = {
    "Interested", "Applied", "RecruiterScreen", "HiringManager",
    "Technical", "OnsiteOrFinal", "Offer", "Closed",
}
VALID_OUTCOMES = {"accepted", "declined", "rejected", "withdrawn"}
VALID_PRIORITIES = {"P0", "P1", "P2"}
VALID_CONTACT_ROLES = {"recruiter", "hiring_manager", "referral", "hr", "other"}
VALID_FUTURE_STATUSES = {"watching", "not_started", "in_research", "ready_to_apply"}

REQUIRED_ACTIVE_FIELDS = {"id", "stage", "priority", "next_action", "next_action_date", "updated_at"}


def err(entry_id: str, msg: str) -> str:
    return f"  [{entry_id}] {msg}"


def validate() -> list[str]:
    errors: list[str] = []

    if not DATA_FILE.exists():
        return [f"File not found: {DATA_FILE}"]

    try:
        with DATA_FILE.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["Root must be a YAML mapping."]

    # --- active[] ---
    active = data.get("active") or []
    seen_ids: set[str] = set()

    for i, entry in enumerate(active):
        eid = entry.get("id") or f"<entry #{i}>"

        if eid in seen_ids:
            errors.append(err(eid, "duplicate id"))
        seen_ids.add(eid)

        for field in REQUIRED_ACTIVE_FIELDS:
            if not entry.get(field):
                errors.append(err(eid, f"missing required field: {field}"))

        stage = entry.get("stage")
        if stage and stage not in VALID_STAGES:
            errors.append(err(eid, f"invalid stage: {stage!r} (expected one of {sorted(VALID_STAGES)})"))

        priority = entry.get("priority")
        if priority and priority not in VALID_PRIORITIES:
            errors.append(err(eid, f"invalid priority: {priority!r}"))

        if stage == "Closed":
            if not entry.get("outcome"):
                errors.append(err(eid, "Closed entry missing outcome"))
            elif entry["outcome"] not in VALID_OUTCOMES:
                errors.append(err(eid, f"invalid outcome: {entry['outcome']!r}"))
            if not entry.get("closed_at"):
                errors.append(err(eid, "Closed entry missing closed_at"))

        contacts = entry.get("contacts") or []
        if not isinstance(contacts, list):
            errors.append(err(eid, "contacts must be a list"))
        else:
            for j, contact in enumerate(contacts):
                cid = contact.get("name") or f"contact #{j}"
                if not contact.get("name"):
                    errors.append(err(eid, f"contact #{j} missing name"))
                role = contact.get("role")
                if role and role not in VALID_CONTACT_ROLES:
                    errors.append(err(eid, f"{cid}: invalid role {role!r} (expected one of {sorted(VALID_CONTACT_ROLES)})"))
                channels = contact.get("channels")
                if channels is not None and not isinstance(channels, dict):
                    errors.append(err(eid, f"{cid}: channels must be a map"))

        links = entry.get("links")
        if links is not None and not isinstance(links, dict):
            errors.append(err(eid, "links must be a map"))

        history = entry.get("history") or []
        if not isinstance(history, list):
            errors.append(err(eid, "history must be a list"))
        elif len(history) > 5:
            errors.append(err(eid, f"history has {len(history)} entries (max 5); drop oldest"))

    # --- future_desired[] ---
    future = data.get("future_desired") or []
    for i, entry in enumerate(future):
        eid = entry.get("id") or f"<future #{i}>"
        if not entry.get("id"):
            errors.append(err(eid, "missing required field: id"))
        status = entry.get("status")
        if status and status not in VALID_FUTURE_STATUSES:
            errors.append(err(eid, f"invalid status: {status!r} (expected one of {sorted(VALID_FUTURE_STATUSES)})"))

    return errors


def main() -> None:
    print(f"Validating {DATA_FILE.relative_to(REPO_ROOT)} ...")
    errors = validate()

    active_count = 0
    future_count = 0
    try:
        with DATA_FILE.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        active_count = len(data.get("active") or [])
        future_count = len(data.get("future_desired") or [])
    except Exception:
        pass

    print(f"  active entries   : {active_count}")
    print(f"  future_desired   : {future_count}")

    if errors:
        print(f"\nFAIL — {len(errors)} error(s):")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("\nOK — all checks passed.")


if __name__ == "__main__":
    main()
