"""Verifies the bundled ``001_init.sql`` migration produces the schema
the rest of the package depends on. Uses the default migration discovery
(``importlib.resources``), not a synthetic temp dir."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from wisp import db


@pytest.fixture
def fresh_conn(tmp_path: Path) -> sqlite3.Connection:
    """A connection with all bundled migrations applied."""
    conn = db.init_db(tmp_path / "x.db")  # default migrations_dir → packaged
    yield conn
    conn.close()


def _table_columns(conn: sqlite3.Connection, table: str) -> dict[str, dict[str, object]]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {
        row["name"]: {
            "type": row["type"],
            "notnull": bool(row["notnull"]),
            "dflt_value": row["dflt_value"],
            "pk": int(row["pk"]),
        }
        for row in rows
    }


EXPECTED_TABLES = {
    "jobs",
    "evaluations",
    "decision_checklist",
    "timeline_events",
    "decisions",
    "signal_overrides",
    "enrichments",
    "schema_migrations",  # created by the migration runner itself
}


def test_all_expected_tables_exist(fresh_conn: sqlite3.Connection) -> None:
    names = {
        row[0]
        for row in fresh_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert EXPECTED_TABLES.issubset(names), names ^ EXPECTED_TABLES


def test_jobs_columns_and_status_index(fresh_conn: sqlite3.Connection) -> None:
    cols = _table_columns(fresh_conn, "jobs")
    expected = {
        "id", "company", "role", "location", "work_type", "employment_type",
        "salary_range", "source", "source_url", "raw_content", "status",
        "created_at", "updated_at",
    }
    assert expected.issubset(cols.keys())
    assert cols["id"]["pk"] == 1

    indexes = {
        row[1]
        for row in fresh_conn.execute("PRAGMA index_list('jobs')")
    }
    assert "idx_jobs_status" in indexes


def test_evaluations_index_on_job_id(fresh_conn: sqlite3.Connection) -> None:
    cols = _table_columns(fresh_conn, "evaluations")
    for required in (
        "kind", "fit_score", "confidence", "signal", "signal_label",
        "brief_recommendation", "brief_reasons_json",
    ):
        assert required in cols, f"missing column: {required}"

    indexes = {
        row[1]
        for row in fresh_conn.execute("PRAGMA index_list('evaluations')")
    }
    assert "idx_evaluations_job_id" in indexes


def test_status_check_constraint_rejects_unknown_status(
    fresh_conn: sqlite3.Connection,
) -> None:
    """jobs.status enforces the documented enum."""
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO jobs (company, role, status) VALUES (?, ?, ?)",
            ("Linear", "Sr Designer", "wishful-thinking"),
        )


def test_signal_check_constraint_rejects_unknown_signal(
    fresh_conn: sqlite3.Connection,
) -> None:
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)",
        ("Linear", "Sr Designer"),
    )
    fresh_conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO evaluations "
            "(job_id, kind, fit_score, confidence, signal, signal_label, "
            " brief_recommendation) "
            "VALUES (?, 'heuristic', 0.5, 0.5, 'unknown', 'x', 'y')",
            (1,),
        )


def test_foreign_key_cascade_deletes_dependent_rows(
    fresh_conn: sqlite3.Connection,
) -> None:
    """Deleting a job also removes its evaluations / timeline / etc."""
    cur = fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)",
        ("Linear", "Sr Designer"),
    )
    job_id = cur.lastrowid
    fresh_conn.execute(
        "INSERT INTO timeline_events (job_id, label, source) "
        "VALUES (?, 'Saved', 'user')",
        (job_id,),
    )
    fresh_conn.execute(
        "INSERT INTO decisions "
        "(job_id, action, signal_at_time, fit_score_at_time, confidence_at_time) "
        "VALUES (?, 'apply', 'yes', 0.8, 0.7)",
        (job_id,),
    )
    fresh_conn.commit()

    fresh_conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    fresh_conn.commit()

    assert (
        fresh_conn.execute(
            "SELECT COUNT(*) FROM timeline_events WHERE job_id = ?", (job_id,)
        ).fetchone()[0]
        == 0
    )
    assert (
        fresh_conn.execute(
            "SELECT COUNT(*) FROM decisions WHERE job_id = ?", (job_id,)
        ).fetchone()[0]
        == 0
    )


def test_decision_checklist_pkey_is_job_id_plus_item_key(
    fresh_conn: sqlite3.Connection,
) -> None:
    """One answer per question per job — re-inserting is rejected."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)",
        ("Linear", "Sr Designer"),
    )
    fresh_conn.commit()
    fresh_conn.execute(
        "INSERT INTO decision_checklist (job_id, item_key, value) "
        "VALUES (1, 'fit', 'yes')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO decision_checklist (job_id, item_key, value) "
            "VALUES (1, 'fit', 'no')"
        )


def test_default_timestamps_are_iso_utc(fresh_conn: sqlite3.Connection) -> None:
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)",
        ("Linear", "Sr Designer"),
    )
    fresh_conn.commit()
    row = fresh_conn.execute("SELECT created_at, updated_at FROM jobs").fetchone()
    # ``YYYY-MM-DDTHH:MM:SS.fffZ`` shape; trailing Z marks UTC
    assert row["created_at"].endswith("Z") and "T" in row["created_at"]
    assert row["updated_at"].endswith("Z") and "T" in row["updated_at"]


def test_migration_recorded_in_schema_migrations(
    fresh_conn: sqlite3.Connection,
) -> None:
    rows = list(
        fresh_conn.execute(
            "SELECT version, name FROM schema_migrations ORDER BY version"
        )
    )
    assert any(r["version"] == 1 and r["name"] == "001_init.sql" for r in rows)


def test_re_running_init_db_is_a_noop(tmp_path: Path) -> None:
    """Calling init_db twice on the same DB shouldn't reapply migrations."""
    path = tmp_path / "x.db"
    conn1 = db.init_db(path)
    conn1.close()

    conn2 = db.connect(path)
    try:
        # No new migration to apply
        assert db.apply_migrations(conn2) == []
        # The migrations table still has exactly the one row
        n = conn2.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert n == 1
    finally:
        conn2.close()
