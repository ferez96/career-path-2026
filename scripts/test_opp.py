#!/usr/bin/env python3
"""
Full test suite for scripts/opp.py

Runs all commands against a temporary YAML fixture — never touches
data/private/opportunities.yaml.

Usage:
    python scripts/test_opp.py [-v]
"""

import io
import os
import sys
import tempfile
import textwrap
import traceback
import unittest
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

import yaml

# ── Locate opp.py and import it ───────────────────────────────────────────────

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))
import opp  # noqa: E402

# ── Fixture data ──────────────────────────────────────────────────────────────

FIXTURE = {
    "schema_version": 1,
    "active": [
        {
            "id": "alpha-senior-backend-2026",
            "company_display": "Alpha Corp",
            "role_title": "Senior Backend Engineer",
            "stage": "Applied",
            "stage_entered_at": "2026-04-01",
            "next_action": "Wait for recruiter feedback.",
            "next_action_date": "2026-05-10",
            "priority": "P0",
            "notes": "Strong fit. Node.js preferred.",
            "updated_at": "2026-04-01",
            "history": [
                "2026-04-01: Applied via portal.",
            ],
            "contacts": [
                {
                    "name": "Jane Doe",
                    "role": "recruiter",
                    "channels": {"linkedin": "https://linkedin.com/in/janedoe"},
                    "notes": "Reached out 2026-04-01",
                }
            ],
            "links": {"job_posting": "https://example.com/job/1"},
        },
        {
            "id": "beta-staff-engineer-2026",
            "company_display": "Beta Inc",
            "role_title": "Staff Engineer",
            "stage": "Interested",
            "next_action": "Tailor CV and apply.",
            "next_action_date": "2026-04-20",  # past date — should show red
            "priority": "P1",
            "notes": "Good domain fit.",
            "updated_at": "2026-04-15",
            "history": [
                "2026-04-15: Added to pipeline.",
            ],
            "contacts": [],
        },
        {
            "id": "closed-role-2026",
            "company_display": "Closed Co",
            "role_title": "Backend Dev",
            "stage": "Closed",
            "stage_entered_at": "2026-04-10",
            "next_action": "N/A",
            "next_action_date": "2026-04-10",
            "priority": "P2",
            "notes": "Salary too low.",
            "outcome": "rejected",
            "closed_at": "2026-04-10",
            "updated_at": "2026-04-10",
            "history": ["2026-04-10: Closed — rejected."],
            "contacts": [],
        },
    ],
    "future_desired": [],
}

# ── Helpers ───────────────────────────────────────────────────────────────────

@contextmanager
def tmp_fixture():
    """Write FIXTURE to a temp file and patch opp.DATA_FILE to point at it."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(FIXTURE, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        tmp_path = Path(f.name)
    try:
        with patch.object(opp, "DATA_FILE", tmp_path):
            yield tmp_path
    finally:
        tmp_path.unlink(missing_ok=True)


def run_cmd(args: list[str]) -> tuple[str, str, int]:
    """
    Run opp.main() with the given CLI args.
    Returns (stdout, stderr, exit_code).
    """
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
        with patch("sys.argv", ["opp"] + args):
            try:
                opp.main()
            except SystemExit as e:
                exit_code = e.code if isinstance(e.code, int) else 1
    return stdout_buf.getvalue(), stderr_buf.getvalue(), exit_code


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_entry(data: dict, entry_id: str) -> dict:
    for e in data.get("active", []):
        if e["id"] == entry_id:
            return e
    raise KeyError(f"id not found: {entry_id}")


# ── Test cases ────────────────────────────────────────────────────────────────

class TestList(unittest.TestCase):

    def test_list_shows_active_only_by_default(self):
        with tmp_fixture():
            out, _, code = run_cmd(["list"])
        self.assertEqual(code, 0)
        self.assertIn("alpha-senior-backend-2026", out)
        self.assertIn("beta-staff-engineer-2026", out)
        self.assertNotIn("closed-role-2026", out)

    def test_list_closed_flag_includes_closed(self):
        with tmp_fixture():
            out, _, code = run_cmd(["list", "--closed"])
        self.assertEqual(code, 0)
        self.assertIn("closed-role-2026", out)

    def test_list_shows_company_names(self):
        with tmp_fixture():
            out, _, code = run_cmd(["list"])
        self.assertIn("Alpha Corp", out)
        self.assertIn("Beta Inc", out)


class TestGet(unittest.TestCase):

    def test_get_exact_id(self):
        with tmp_fixture():
            out, _, code = run_cmd(["get", "alpha-senior-backend-2026"])
        self.assertEqual(code, 0)
        self.assertIn("Alpha Corp", out)
        self.assertIn("Senior Backend Engineer", out)

    def test_get_prefix_match(self):
        with tmp_fixture():
            out, _, code = run_cmd(["get", "alpha"])
        self.assertEqual(code, 0)
        self.assertIn("Alpha Corp", out)

    def test_get_ambiguous_prefix_exits_nonzero(self):
        # both "alpha" and "beta" start with their names, but "a" is unambiguous here
        # make an ambiguous case: prefix "beta" is unique, but prefix "-" matches all
        with tmp_fixture():
            _, err, code = run_cmd(["get", "-"])
        # dash not a prefix of any id → not found (code 1)
        self.assertNotEqual(code, 0)

    def test_get_not_found_exits_nonzero(self):
        with tmp_fixture():
            _, err, code = run_cmd(["get", "nonexistent-id"])
        self.assertNotEqual(code, 0)
        self.assertIn("nonexistent-id", err)

    def test_get_shows_contacts(self):
        with tmp_fixture():
            out, _, code = run_cmd(["get", "alpha"])
        self.assertIn("Jane Doe", out)

    def test_get_shows_history(self):
        with tmp_fixture():
            out, _, code = run_cmd(["get", "alpha"])
        self.assertIn("Applied via portal", out)

    def test_get_shows_links(self):
        with tmp_fixture():
            out, _, code = run_cmd(["get", "alpha"])
        self.assertIn("job_posting", out)


class TestStage(unittest.TestCase):

    def test_stage_transition_updates_file(self):
        with tmp_fixture() as path:
            _, _, code = run_cmd(["stage", "alpha", "RecruiterScreen"])
            self.assertEqual(code, 0)
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        self.assertEqual(entry["stage"], "RecruiterScreen")
        self.assertEqual(entry["stage_entered_at"], opp.TODAY)
        self.assertEqual(entry["updated_at"], opp.TODAY)

    def test_stage_appends_history(self):
        with tmp_fixture() as path:
            run_cmd(["stage", "alpha", "RecruiterScreen"])
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        self.assertTrue(any("RecruiterScreen" in h for h in entry["history"]))

    def test_stage_invalid_exits_nonzero(self):
        with tmp_fixture():
            _, err, code = run_cmd(["stage", "alpha", "NotAStage"])
        self.assertNotEqual(code, 0)

    def test_stage_close_without_outcome_exits_nonzero(self):
        with tmp_fixture():
            _, err, code = run_cmd(["stage", "alpha", "Closed"])
        self.assertNotEqual(code, 0)
        self.assertIn("outcome", err)

    def test_stage_close_with_outcome(self):
        with tmp_fixture() as path:
            _, _, code = run_cmd(["stage", "alpha", "Closed", "--outcome", "rejected"])
            self.assertEqual(code, 0)
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        self.assertEqual(entry["stage"], "Closed")
        self.assertEqual(entry["outcome"], "rejected")
        self.assertEqual(entry["closed_at"], opp.TODAY)


class TestNext(unittest.TestCase):

    def test_next_updates_date_and_action(self):
        with tmp_fixture() as path:
            _, _, code = run_cmd(["next", "alpha", "2026-06-01", "Send follow-up email."])
            self.assertEqual(code, 0)
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        self.assertEqual(entry["next_action_date"], "2026-06-01")
        self.assertEqual(entry["next_action"], "Send follow-up email.")
        self.assertEqual(entry["updated_at"], opp.TODAY)

    def test_next_does_not_touch_other_entries(self):
        with tmp_fixture() as path:
            run_cmd(["next", "alpha", "2026-06-01", "Follow up."])
            data = load_yaml(path)
            entry = find_entry(data, "beta-staff-engineer-2026")
        self.assertEqual(entry["next_action"], "Tailor CV and apply.")


class TestClose(unittest.TestCase):

    def test_close_sets_all_fields(self):
        with tmp_fixture() as path:
            _, _, code = run_cmd(["close", "beta", "withdrawn", "--note", "Changed priorities."])
            self.assertEqual(code, 0)
            data = load_yaml(path)
            entry = find_entry(data, "beta-staff-engineer-2026")
        self.assertEqual(entry["stage"], "Closed")
        self.assertEqual(entry["outcome"], "withdrawn")
        self.assertEqual(entry["closed_at"], opp.TODAY)
        self.assertTrue(any("withdrawn" in h for h in entry["history"]))

    def test_close_invalid_outcome_exits_nonzero(self):
        with tmp_fixture():
            _, err, code = run_cmd(["close", "beta", "ghosted"])
        self.assertNotEqual(code, 0)

    def test_close_note_appears_in_history(self):
        with tmp_fixture() as path:
            run_cmd(["close", "beta", "declined", "--note", "Salary too low."])
            data = load_yaml(path)
            entry = find_entry(data, "beta-staff-engineer-2026")
        self.assertTrue(any("Salary too low" in h for h in entry["history"]))


class TestNote(unittest.TestCase):

    def test_note_appended_with_date_prefix(self):
        with tmp_fixture() as path:
            _, _, code = run_cmd(["note", "alpha", "Recruiter called back."])
            self.assertEqual(code, 0)
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        last = entry["history"][-1]
        self.assertIn(opp.TODAY, last)
        self.assertIn("Recruiter called back", last)

    def test_note_no_duplicate_date_prefix(self):
        """If note already starts with today, don't prepend again."""
        with tmp_fixture() as path:
            run_cmd(["note", "alpha", f"{opp.TODAY}: Already dated."])
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        last = entry["history"][-1]
        # Should not have date appear twice
        self.assertEqual(last.count(opp.TODAY), 1)

    def test_history_capped_at_max(self):
        """history should not exceed HISTORY_MAX (5) entries."""
        with tmp_fixture() as path:
            for i in range(10):
                run_cmd(["note", "alpha", f"Note number {i}."])
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        self.assertLessEqual(len(entry["history"]), opp.HISTORY_MAX)

    def test_history_keeps_most_recent(self):
        """When capped, the oldest entries are dropped, newest retained."""
        with tmp_fixture() as path:
            for i in range(10):
                run_cmd(["note", "alpha", f"Note {i}."])
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        last = entry["history"][-1]
        self.assertIn("Note 9", last)


class TestSet(unittest.TestCase):

    def test_set_valid_field(self):
        with tmp_fixture() as path:
            _, _, code = run_cmd(["set", "alpha", "priority", "P2"])
            self.assertEqual(code, 0)
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        self.assertEqual(entry["priority"], "P2")
        self.assertEqual(entry["updated_at"], opp.TODAY)

    def test_set_notes(self):
        with tmp_fixture() as path:
            run_cmd(["set", "alpha", "notes", "Updated notes content."])
            data = load_yaml(path)
            entry = find_entry(data, "alpha-senior-backend-2026")
        self.assertEqual(entry["notes"], "Updated notes content.")

    def test_set_invalid_field_exits_nonzero(self):
        with tmp_fixture():
            _, err, code = run_cmd(["set", "alpha", "contacts", "[]"])
        self.assertNotEqual(code, 0)
        self.assertIn("not a settable scalar field", err)

    def test_set_does_not_touch_other_entries(self):
        with tmp_fixture() as path:
            run_cmd(["set", "alpha", "priority", "P2"])
            data = load_yaml(path)
            entry = find_entry(data, "beta-staff-engineer-2026")
        self.assertEqual(entry["priority"], "P1")


class TestFields(unittest.TestCase):

    def test_fields_exits_zero(self):
        with tmp_fixture():
            _, _, code = run_cmd(["fields"])
        self.assertEqual(code, 0)

    def test_fields_lists_known_fields(self):
        with tmp_fixture():
            out, _, _ = run_cmd(["fields"])
        for f in ["priority", "stage", "next_action", "notes", "outcome"]:
            self.assertIn(f, out)


class TestAtomicWrite(unittest.TestCase):

    def test_file_unchanged_on_same_id_set(self):
        """File mtime should change after a write."""
        import time
        with tmp_fixture() as path:
            mtime_before = path.stat().st_mtime
            time.sleep(0.05)
            run_cmd(["set", "alpha", "priority", "P1"])
            mtime_after = path.stat().st_mtime
        self.assertGreater(mtime_after, mtime_before)

    def test_other_entries_preserved_after_write(self):
        """All other entries must survive a targeted edit."""
        with tmp_fixture() as path:
            run_cmd(["set", "alpha", "priority", "P2"])
            data = load_yaml(path)
        ids = [e["id"] for e in data["active"]]
        self.assertIn("beta-staff-engineer-2026", ids)
        self.assertIn("closed-role-2026", ids)
        self.assertEqual(len(ids), 3)

    def test_schema_version_preserved(self):
        with tmp_fixture() as path:
            run_cmd(["set", "alpha", "priority", "P2"])
            data = load_yaml(path)
        self.assertEqual(data.get("schema_version"), 1)

    def test_future_desired_preserved(self):
        with tmp_fixture() as path:
            run_cmd(["note", "alpha", "Some note."])
            data = load_yaml(path)
        self.assertIn("future_desired", data)


class TestPrefixMatching(unittest.TestCase):

    def test_exact_match_preferred_over_prefix(self):
        """If a full id is provided, use it even if it's a prefix of another."""
        with tmp_fixture() as path:
            # "alpha-senior-backend-2026" is a full id
            _, _, code = run_cmd(["get", "alpha-senior-backend-2026"])
        self.assertEqual(code, 0)

    def test_ambiguous_prefix_exits_nonzero(self):
        # "2026" is a suffix of all ids — but as a prefix it matches nothing
        # Use something that IS a prefix of multiple: none in our fixture
        # Inject a fixture with two ids sharing a prefix
        ambiguous_fixture = {
            "schema_version": 1,
            "active": [
                {
                    "id": "same-prefix-alpha-2026",
                    "company_display": "A",
                    "role_title": "R",
                    "stage": "Interested",
                    "next_action": "x",
                    "next_action_date": "2026-06-01",
                    "priority": "P1",
                    "notes": "",
                    "updated_at": "2026-05-01",
                    "history": [],
                    "contacts": [],
                },
                {
                    "id": "same-prefix-beta-2026",
                    "company_display": "B",
                    "role_title": "R",
                    "stage": "Interested",
                    "next_action": "x",
                    "next_action_date": "2026-06-01",
                    "priority": "P1",
                    "notes": "",
                    "updated_at": "2026-05-01",
                    "history": [],
                    "contacts": [],
                },
            ],
            "future_desired": [],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(ambiguous_fixture, f)
            tmp_path = Path(f.name)
        try:
            with patch.object(opp, "DATA_FILE", tmp_path):
                _, err, code = run_cmd(["get", "same-prefix"])
            self.assertNotEqual(code, 0)
            self.assertIn("ambiguous", err)
        finally:
            tmp_path.unlink(missing_ok=True)


# ── Runner ────────────────────────────────────────────────────────────────────

class _ColorResult(unittest.TextTestResult):
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def addSuccess(self, test):
        super().addSuccess(test)
        if self.showAll:
            self.stream.writeln(f"{self.GREEN}PASS{self.RESET}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.showAll:
            self.stream.writeln(f"{self.RED}FAIL{self.RESET}")

    def addError(self, test, err):
        super().addError(test, err)
        if self.showAll:
            self.stream.writeln(f"{self.RED}ERROR{self.RESET}")


class _ColorRunner(unittest.TextTestRunner):
    resultclass = _ColorResult


if __name__ == "__main__":
    verbose = "-v" in sys.argv
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = _ColorRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
