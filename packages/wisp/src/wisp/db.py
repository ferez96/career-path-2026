"""SQLite connection + numbered-migrations runner.

The DB lives at ``config.db_path()`` (under ``WISP_DATA_DIR``). Every
opened connection has WAL mode, foreign keys, and a sensible busy timeout
applied via :func:`connect`.

Migrations are plain ``.sql`` files named ``NNN_description.sql`` shipped
inside the package at :mod:`wisp.migrations`. :func:`apply_migrations`
runs them in order, tracks applied versions in a ``schema_migrations``
table, and is idempotent — calling it twice does no extra work.

Authoring migrations
--------------------
* Use ``CREATE TABLE IF NOT EXISTS`` (and ``CREATE INDEX IF NOT EXISTS``)
  so a partial application is safely re-runnable. The runner records the
  version row in a *separate* small transaction immediately after the
  migration's SQL succeeds — if that SQL raises mid-way, no version is
  recorded and the next run replays the whole file.
* Default values, especially timestamps, should match the convention in
  ``001_init.sql`` (ISO-8601 UTC via ``strftime('%Y-%m-%dT%H:%M:%fZ','now')``).
* For empty / unknown text fields prefer ``NULL`` over ``''``.
* For domain enums, only add a ``CHECK`` constraint when the value
  actually drives logic (e.g. ``jobs.status`` drives the list filter,
  ``evaluations.signal`` drives label generation). Informational fields
  (sources, types, statuses-of-things) get no ``CHECK`` and the app
  validates on the way in. This keeps schema evolution cheap.

Widening a kept CHECK constraint
--------------------------------
SQLite has no ``ALTER TABLE … MODIFY CONSTRAINT``, so adding a new value
to a retained ``CHECK`` requires the canonical four-step rebuild — write
it as ``002_widen_xxx.sql`` (or similar):

  1. ``CREATE TABLE jobs_new (… new CHECK …)``
  2. ``INSERT INTO jobs_new SELECT * FROM jobs``
  3. ``DROP TABLE jobs``
  4. ``ALTER TABLE jobs_new RENAME TO jobs``
  5. Recreate any indexes / triggers that referenced the old table name.

Wrap the whole thing in ``BEGIN; … COMMIT;`` so a partial failure leaves
the original table intact.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable
from importlib import resources
from pathlib import Path

from . import config

# ``NNN_description.sql`` — three+ digits, underscore, anything ending .sql
_MIGRATION_NAME_RE = re.compile(r"^(\d+)_[A-Za-z0-9_\-]+\.sql$")


def connect(path: Path | None = None) -> sqlite3.Connection:
    """Open a SQLite connection at ``path`` (or :func:`config.db_path()`).

    Tuning rationale:
      * ``Row`` factory so callers can use column-name access.
      * ``foreign_keys = ON`` — SQLite leaves them off by default.
      * ``journal_mode = WAL`` — readers don't block writers; safe for our
        single-process desktop app and survives ``kill -9`` better than
        rollback journal mode.
      * ``synchronous = NORMAL`` — recommended companion to WAL; durable
        across OS crashes (just not power loss without battery / FBWC).
      * ``timeout = 5.0`` — block briefly on writer lock instead of
        immediately raising ``sqlite3.OperationalError``.
    """
    target = path if path is not None else config.db_path()
    # Default isolation (deferred); we manage commits explicitly per
    # migration. Avoid ``isolation_level=None`` because ``executescript``
    # in autocommit mode skips Python's transaction tracking and breaks
    # our BEGIN/COMMIT bookkeeping.
    conn = sqlite3.connect(target, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.commit()  # PRAGMAs run in their own implicit transaction
    return conn


def _ensure_schema_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version    INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )


def _applied_versions(conn: sqlite3.Connection) -> set[int]:
    return {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}


def _discover_migrations(migrations_dir: Path | None) -> list[tuple[int, str, str]]:
    """Return ``(version, name, sql)`` triples sorted by version.

    If ``migrations_dir`` is ``None``, read from the packaged
    ``wisp.migrations`` resource so the wheel works post-install.
    """
    found: list[tuple[int, str, str]] = []
    if migrations_dir is not None:
        for sql_path in sorted(migrations_dir.glob("*.sql")):
            m = _MIGRATION_NAME_RE.match(sql_path.name)
            if not m:
                continue
            found.append((int(m.group(1)), sql_path.name, sql_path.read_text(encoding="utf-8")))
    else:
        package = resources.files("wisp.migrations")
        for entry in sorted(package.iterdir(), key=lambda p: p.name):
            m = _MIGRATION_NAME_RE.match(entry.name)
            if not m:
                continue
            found.append((int(m.group(1)), entry.name, entry.read_text(encoding="utf-8")))
    found.sort(key=lambda t: t[0])
    _check_unique_versions(found)
    return found


def _check_unique_versions(items: Iterable[tuple[int, str, str]]) -> None:
    seen: dict[int, str] = {}
    for version, name, _sql in items:
        if version in seen:
            raise RuntimeError(
                f"Duplicate migration version {version}: "
                f"{seen[version]!r} and {name!r}"
            )
        seen[version] = name


def apply_migrations(
    conn: sqlite3.Connection,
    migrations_dir: Path | None = None,
) -> list[int]:
    """Apply any pending migrations. Returns the versions applied this call.

    Idempotent: a second call with no new migration files does nothing and
    returns ``[]``. If a migration's SQL raises, the corresponding
    ``schema_migrations`` row is *not* inserted, so the next run will
    re-attempt that migration. Author migrations with ``IF NOT EXISTS``
    guards (or ``BEGIN; ... COMMIT;`` wrapping) so partial failures are
    safely re-runnable.
    """
    _ensure_schema_migrations_table(conn)
    conn.commit()
    applied = _applied_versions(conn)
    pending = [m for m in _discover_migrations(migrations_dir) if m[0] not in applied]
    newly_applied: list[int] = []
    for version, name, sql in pending:
        # ``executescript`` issues its own COMMIT before running and then
        # executes the script in autocommit. We can't wrap it in a Python
        # transaction; instead we record the version in a separate, small
        # transaction immediately after, so a failure inside the migration
        # SQL leaves no ``schema_migrations`` row and the next run replays
        # the migration.
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
            (version, name),
        )
        conn.commit()
        newly_applied.append(version)
    return newly_applied


def init_db(
    path: Path | None = None,
    migrations_dir: Path | None = None,
) -> sqlite3.Connection:
    """Open the DB and bring its schema up to date.

    Convenience over :func:`connect` + :func:`apply_migrations` for the
    common case of "give me a ready-to-use connection".
    """
    conn = connect(path)
    apply_migrations(conn, migrations_dir)
    return conn
