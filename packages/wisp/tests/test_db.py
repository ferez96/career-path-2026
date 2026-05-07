"""Tests for ``wisp.db`` — connection pragmas, migration discovery,
idempotent application, ordering, transaction rollback."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from wisp import db


def _write(dir_: Path, name: str, sql: str) -> None:
    (dir_ / name).write_text(sql, encoding="utf-8")


def test_connect_applies_expected_pragmas(tmp_path: Path) -> None:
    conn = db.connect(tmp_path / "x.db")
    try:
        # foreign_keys returns 1 when ON
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        # WAL mode reports the new mode after the PRAGMA assignment
        assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        # synchronous: 0=OFF, 1=NORMAL, 2=FULL, 3=EXTRA
        assert conn.execute("PRAGMA synchronous").fetchone()[0] == 1
        # Row factory is dict-like
        row = conn.execute("SELECT 7 AS n").fetchone()
        assert row["n"] == 7
    finally:
        conn.close()


def test_apply_migrations_runs_each_once(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    _write(migrations, "001_a.sql", "CREATE TABLE a (id INTEGER PRIMARY KEY);")
    _write(migrations, "002_b.sql", "CREATE TABLE b (id INTEGER PRIMARY KEY);")

    conn = db.connect(tmp_path / "x.db")
    try:
        first = db.apply_migrations(conn, migrations)
        assert first == [1, 2]

        # Second run is a no-op
        second = db.apply_migrations(conn, migrations)
        assert second == []

        # Both tables exist
        names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "ORDER BY name"
            )
        }
        assert {"a", "b"}.issubset(names)
    finally:
        conn.close()


def test_apply_migrations_runs_in_version_order(tmp_path: Path) -> None:
    """File-system listing order must NOT determine apply order."""
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    # Write out-of-order so glob() returns them lexicographically; runner
    # must sort by parsed version int (gap-tolerant).
    _write(migrations, "010_b.sql", "CREATE TABLE b (id INTEGER);")
    _write(migrations, "002_a.sql", "CREATE TABLE a (id INTEGER);")

    conn = db.connect(tmp_path / "x.db")
    try:
        applied = db.apply_migrations(conn, migrations)
        assert applied == [2, 10]
        order = [
            row["version"]
            for row in conn.execute(
                "SELECT version FROM schema_migrations ORDER BY applied_at"
            )
        ]
        assert order == [2, 10]
    finally:
        conn.close()


def test_apply_migrations_picks_up_new_files_on_second_call(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    _write(migrations, "001_a.sql", "CREATE TABLE a (id INTEGER);")

    conn = db.connect(tmp_path / "x.db")
    try:
        assert db.apply_migrations(conn, migrations) == [1]

        # Add a new migration; second call should apply only it
        _write(migrations, "002_b.sql", "CREATE TABLE b (id INTEGER);")
        assert db.apply_migrations(conn, migrations) == [2]
    finally:
        conn.close()


def test_apply_migrations_rolls_back_on_failure(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    _write(migrations, "001_a.sql", "CREATE TABLE a (id INTEGER);")
    # Migration 002 is broken — references a column that doesn't exist
    _write(migrations, "002_bad.sql", "INSERT INTO does_not_exist VALUES (1);")

    conn = db.connect(tmp_path / "x.db")
    try:
        with pytest.raises(sqlite3.OperationalError):
            db.apply_migrations(conn, migrations)

        # 001 is committed; 002 is not recorded
        applied = {row["version"] for row in conn.execute("SELECT version FROM schema_migrations")}
        assert applied == {1}
    finally:
        conn.close()


def test_duplicate_migration_versions_are_rejected(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    _write(migrations, "001_a.sql", "CREATE TABLE a (id INTEGER);")
    _write(migrations, "001_dup.sql", "CREATE TABLE dup (id INTEGER);")

    conn = db.connect(tmp_path / "x.db")
    try:
        with pytest.raises(RuntimeError, match="Duplicate migration version 1"):
            db.apply_migrations(conn, migrations)
    finally:
        conn.close()


def test_non_migration_files_are_ignored(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    _write(migrations, "001_a.sql", "CREATE TABLE a (id INTEGER);")
    # Unrelated files in the dir
    _write(migrations, "README.md", "# notes")
    _write(migrations, "bad-name.sql", "CREATE TABLE bad (id INTEGER);")

    conn = db.connect(tmp_path / "x.db")
    try:
        assert db.apply_migrations(conn, migrations) == [1]
    finally:
        conn.close()


def test_init_db_returns_ready_connection(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    _write(migrations, "001_a.sql", "CREATE TABLE a (id INTEGER PRIMARY KEY, name TEXT);")

    conn = db.init_db(tmp_path / "x.db", migrations)
    try:
        conn.execute("INSERT INTO a (name) VALUES (?)", ("alice",))
        row = conn.execute("SELECT name FROM a WHERE id = 1").fetchone()
        assert row["name"] == "alice"
    finally:
        conn.close()


def test_init_db_uses_config_db_path_by_default(isolated_wisp_data_dir: Path) -> None:
    """No explicit path → goes via config.db_path() which respects WISP_DATA_DIR."""
    from wisp import config as cfg_mod

    migrations = isolated_wisp_data_dir / "migrations"
    migrations.mkdir()
    _write(migrations, "001_a.sql", "CREATE TABLE a (id INTEGER);")

    conn = db.init_db(migrations_dir=migrations)
    try:
        assert cfg_mod.db_path().exists()
    finally:
        conn.close()
