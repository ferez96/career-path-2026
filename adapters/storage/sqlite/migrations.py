"""SQLite schema bootstrap for token monitoring."""

from __future__ import annotations

import sqlite3


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS usage_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    task_type TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    cached_tokens INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    cost_total REAL NOT NULL DEFAULT 0,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    request_id TEXT,
    error_message TEXT,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_usage_events_ts ON usage_events(ts);
CREATE INDEX IF NOT EXISTS idx_usage_events_task ON usage_events(task_type);
CREATE INDEX IF NOT EXISTS idx_usage_events_model ON usage_events(model);

CREATE TABLE IF NOT EXISTS monthly_rollups (
    month TEXT NOT NULL,
    task_type TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    requests INTEGER NOT NULL DEFAULT 0,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    cached_tokens INTEGER NOT NULL DEFAULT 0,
    total_cost REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (month, task_type, provider, model)
);

CREATE TABLE IF NOT EXISTS budget_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    scope_type TEXT NOT NULL,
    scope_value TEXT NOT NULL,
    limit_usd REAL NOT NULL,
    current_usd REAL NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    triggered_at TEXT NOT NULL,
    UNIQUE (month, scope_type, scope_value)
);

CREATE INDEX IF NOT EXISTS idx_budget_alerts_month_status
ON budget_alerts(month, status);
"""


def bootstrap_schema(connection: sqlite3.Connection) -> None:
    """Create all tables and indexes if missing."""
    connection.executescript(SCHEMA_SQL)
    connection.commit()

