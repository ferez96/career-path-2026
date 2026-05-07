"""Verifies the bundled ``001_init.sql`` migration produces the schema
the rest of the package depends on. Uses the default migration discovery
(``importlib.resources``), not a synthetic temp dir."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from wisp import db


@pytest.fixture
def fresh_conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    """A connection with all bundled migrations applied."""
    conn = db.init_db(tmp_path / "x.db")  # default migrations_dir → packaged
    try:
        yield conn
    finally:
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


def _index_names(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA index_list('{table}')")}


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


# ---- jobs ------------------------------------------------------------------


def test_jobs_has_structured_salary_columns(fresh_conn: sqlite3.Connection) -> None:
    """The M3.4 heuristic compares against numeric salary fields, not the
    display string. Currency is required and defaults to USD."""
    cols = _table_columns(fresh_conn, "jobs")
    assert "salary_min" in cols and cols["salary_min"]["type"] == "INTEGER"
    assert "salary_max" in cols and cols["salary_max"]["type"] == "INTEGER"
    assert "salary_currency" in cols
    assert cols["salary_currency"]["notnull"] is True
    assert cols["salary_currency"]["dflt_value"] == "'USD'"
    # Numeric salary fields are nullable so JDs we can't parse don't break.
    assert cols["salary_min"]["notnull"] is False
    assert cols["salary_max"]["notnull"] is False


def test_jobs_optional_text_fields_default_to_null(
    fresh_conn: sqlite3.Connection,
) -> None:
    """Per the NULL-as-empty convention, location / work_type / etc. are
    nullable and have no '' default."""
    cols = _table_columns(fresh_conn, "jobs")
    for nullable in (
        "location", "work_type", "employment_type", "salary_range",
        "source", "source_url", "raw_content",
    ):
        assert cols[nullable]["notnull"] is False, f"{nullable} should be nullable"
        assert cols[nullable]["dflt_value"] is None, f"{nullable} should have no default"


def test_jobs_status_check_still_enforced(fresh_conn: sqlite3.Connection) -> None:
    """status drives the list filter and /overview tiles — keep its CHECK."""
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO jobs (company, role, status) VALUES (?, ?, ?)",
            ("Linear", "Sr Designer", "wishful-thinking"),
        )


def test_jobs_work_type_now_accepts_unknown_values(
    fresh_conn: sqlite3.Connection,
) -> None:
    """work_type CHECK was dropped — the app validates, not the DB.
    This lets us add 'flex' or 'co-op' without a table rebuild."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role, work_type) VALUES (?, ?, ?)",
        ("Linear", "Sr Designer", "flex-anywhere"),
    )
    fresh_conn.commit()
    row = fresh_conn.execute("SELECT work_type FROM jobs WHERE id=1").fetchone()
    assert row["work_type"] == "flex-anywhere"


def test_jobs_status_index_exists(fresh_conn: sqlite3.Connection) -> None:
    assert "idx_jobs_status" in _index_names(fresh_conn, "jobs")


# ---- evaluations -----------------------------------------------------------


def test_evaluations_kind_signal_score_checks_enforced(
    fresh_conn: sqlite3.Connection,
) -> None:
    """kind / signal / fit_score / confidence drive logic — keep their CHECKs."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "Sr Designer")
    )
    fresh_conn.commit()

    # bad signal
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO evaluations "
            "(job_id, kind, fit_score, confidence, signal, signal_label) "
            "VALUES (1, 'heuristic', 0.5, 0.5, 'unknown', 'x')"
        )
    # bad kind
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO evaluations "
            "(job_id, kind, fit_score, confidence, signal, signal_label) "
            "VALUES (1, 'rule-based', 0.5, 0.5, 'yes', 'x')"
        )
    # fit_score out of range
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO evaluations "
            "(job_id, kind, fit_score, confidence, signal, signal_label) "
            "VALUES (1, 'heuristic', 1.7, 0.5, 'yes', 'x')"
        )


def test_evaluations_brief_recommendation_can_be_null(
    fresh_conn: sqlite3.Connection,
) -> None:
    """Heuristic-only paths may leave brief_recommendation NULL; the UI
    falls back to signal_label."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
    )
    fresh_conn.execute(
        "INSERT INTO evaluations "
        "(job_id, kind, fit_score, confidence, signal, signal_label) "
        "VALUES (1, 'heuristic', 0.5, 0.5, 'pending', 'Need more info')"
    )
    fresh_conn.commit()
    row = fresh_conn.execute("SELECT brief_recommendation FROM evaluations").fetchone()
    assert row["brief_recommendation"] is None


def test_evaluations_indexes(fresh_conn: sqlite3.Connection) -> None:
    indexes = _index_names(fresh_conn, "evaluations")
    assert "idx_evaluations_job_id" in indexes
    # Hot-list query: latest <kind> for each job
    assert "idx_evaluations_job_kind_time" in indexes
    # Pending-filter MAX(id) subquery (added by 002_pending_filter_index.sql)
    assert "idx_evaluations_job_kind_id" in indexes


def test_pending_filter_subquery_uses_new_index(
    fresh_conn: sqlite3.Connection,
) -> None:
    """EXPLAIN QUERY PLAN should mention idx_evaluations_job_kind_id for
    the MAX(id) subquery — proves the index actually wins over the others."""
    plan = fresh_conn.execute(
        """
        EXPLAIN QUERY PLAN
        SELECT MAX(e2.id) FROM evaluations e2
        WHERE e2.job_id = 1 AND e2.kind = 'composite'
        """
    ).fetchall()
    plan_text = " | ".join(row["detail"] for row in plan)
    assert "idx_evaluations_job_kind_id" in plan_text, plan_text


# ---- decision_checklist ----------------------------------------------------


def test_decision_checklist_value_no_longer_constrained(
    fresh_conn: sqlite3.Connection,
) -> None:
    """value CHECK was dropped — the UI may switch from yes/maybe/no
    to a 1-5 scale without a schema migration."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
    )
    fresh_conn.execute(
        "INSERT INTO decision_checklist (job_id, item_key, value) "
        "VALUES (1, 'fit', '4')"  # 1-5 scale
    )
    fresh_conn.commit()
    row = fresh_conn.execute(
        "SELECT value FROM decision_checklist WHERE job_id=1 AND item_key='fit'"
    ).fetchone()
    assert row["value"] == "4"


def test_decision_checklist_pkey_is_job_id_plus_item_key(
    fresh_conn: sqlite3.Connection,
) -> None:
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
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


# ---- timeline_events -------------------------------------------------------


def test_timeline_events_source_no_longer_constrained(
    fresh_conn: sqlite3.Connection,
) -> None:
    """source CHECK was dropped — new tags ('cron', 'gmail', ...) land
    without rebuild."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
    )
    fresh_conn.execute(
        "INSERT INTO timeline_events (job_id, label, source) "
        "VALUES (1, 'Auto-fetched', 'cron')"
    )
    fresh_conn.commit()


# ---- decisions / overrides -------------------------------------------------


def test_decisions_action_check_still_enforced(
    fresh_conn: sqlite3.Connection,
) -> None:
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
    )
    fresh_conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO decisions "
            "(job_id, action, signal_at_time, fit_score_at_time, confidence_at_time) "
            "VALUES (1, 'ghost', 'yes', 0.5, 0.5)"
        )


def test_signal_overrides_both_signals_constrained(
    fresh_conn: sqlite3.Connection,
) -> None:
    """Both original_signal and user_signal carry CHECKs — symmetric."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
    )
    fresh_conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO signal_overrides "
            "(job_id, original_signal, user_signal) VALUES (1, 'wishful', 'yes')"
        )
    with pytest.raises(sqlite3.IntegrityError):
        fresh_conn.execute(
            "INSERT INTO signal_overrides "
            "(job_id, original_signal, user_signal) VALUES (1, 'yes', 'wishful')"
        )


# ---- enrichments -----------------------------------------------------------


def test_enrichments_no_longer_has_by_user_column(
    fresh_conn: sqlite3.Connection,
) -> None:
    """`by_user` was always 1 in v1 — dropped until automation lands."""
    cols = _table_columns(fresh_conn, "enrichments")
    assert "by_user" not in cols


def test_enrichments_result_json_is_nullable(fresh_conn: sqlite3.Connection) -> None:
    """No '{}' default — providers may emit lists, NULL means 'no result yet'."""
    cols = _table_columns(fresh_conn, "enrichments")
    assert cols["result_json"]["notnull"] is False
    assert cols["result_json"]["dflt_value"] is None


def test_enrichments_source_no_longer_constrained(
    fresh_conn: sqlite3.Connection,
) -> None:
    """New AI provider categories (e.g. 'local' for Ollama) drop in
    without a schema migration."""
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
    )
    fresh_conn.execute(
        "INSERT INTO enrichments (job_id, provider_key, source) "
        "VALUES (1, 'ollama_summary', 'local')"
    )
    fresh_conn.commit()


# ---- general ---------------------------------------------------------------


def test_foreign_key_cascade_deletes_dependent_rows(
    fresh_conn: sqlite3.Connection,
) -> None:
    """Deleting a job also removes its evaluations / timeline / etc."""
    cur = fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
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


def test_default_timestamps_are_iso_utc(fresh_conn: sqlite3.Connection) -> None:
    fresh_conn.execute(
        "INSERT INTO jobs (company, role) VALUES (?, ?)", ("Linear", "x")
    )
    fresh_conn.commit()
    row = fresh_conn.execute("SELECT created_at, updated_at FROM jobs").fetchone()
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
    path = tmp_path / "x.db"
    conn1 = db.init_db(path)
    before = conn1.execute(
        "SELECT COUNT(*) FROM schema_migrations"
    ).fetchone()[0]
    conn1.close()

    conn2 = db.connect(path)
    try:
        assert db.apply_migrations(conn2) == []  # no new migrations applied
        after = conn2.execute(
            "SELECT COUNT(*) FROM schema_migrations"
        ).fetchone()[0]
        assert after == before  # row count unchanged
    finally:
        conn2.close()
