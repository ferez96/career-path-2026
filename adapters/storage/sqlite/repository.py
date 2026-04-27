"""SQLite repository for usage telemetry and rollups."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from adapters.storage.sqlite.migrations import bootstrap_schema
from core.cost.budget import BudgetAlert
from core.types import UsageEvent


class TokenUsageRepository:
    """Persistence layer for token usage and budget monitoring.

    Each thread gets its own SQLite connection via threading.local so this
    repository is safe to share across a multi-threaded HTTP server.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        # Bootstrap schema on the calling (main) thread connection.
        bootstrap_schema(self._conn)

    @property
    def _conn(self) -> sqlite3.Connection:
        """Return a per-thread SQLite connection, creating it if needed."""
        conn = getattr(self._local, "connection", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self._local.connection = conn
        return conn

    def close(self) -> None:
        """Close the connection on the current thread, if open."""
        conn = getattr(self._local, "connection", None)
        if conn is not None:
            conn.close()
            self._local.connection = None

    def insert_usage_event(self, event: UsageEvent, total_cost: float) -> int:
        month = event.ts.strftime("%Y-%m")
        cursor = self._conn.execute(
            """
            INSERT INTO usage_events (
                ts, task_type, provider, model,
                input_tokens, output_tokens, cached_tokens, duration_ms,
                cost_total, source, status, request_id, error_message, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.ts.isoformat(),
                event.task_type,
                event.provider,
                event.model,
                event.input_tokens,
                event.output_tokens,
                event.cached_tokens,
                event.duration_ms,
                total_cost,
                event.source,
                event.status,
                event.request_id,
                event.error_message,
                json.dumps(event.metadata, ensure_ascii=True),
            ),
        )
        self._conn.execute(
            """
            INSERT INTO monthly_rollups (
                month, task_type, provider, model,
                requests, input_tokens, output_tokens, cached_tokens, total_cost
            )
            VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
            ON CONFLICT(month, task_type, provider, model)
            DO UPDATE SET
                requests = requests + 1,
                input_tokens = input_tokens + excluded.input_tokens,
                output_tokens = output_tokens + excluded.output_tokens,
                cached_tokens = cached_tokens + excluded.cached_tokens,
                total_cost = total_cost + excluded.total_cost
            """,
            (
                month,
                event.task_type,
                event.provider,
                event.model,
                event.input_tokens,
                event.output_tokens,
                event.cached_tokens,
                total_cost,
            ),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def recompute_monthly_rollups(self) -> None:
        self._conn.execute("DELETE FROM monthly_rollups")
        self._conn.execute(
            """
            INSERT INTO monthly_rollups (
                month, task_type, provider, model,
                requests, input_tokens, output_tokens, cached_tokens, total_cost
            )
            SELECT
                substr(ts, 1, 7) AS month,
                task_type,
                provider,
                model,
                COUNT(*) AS requests,
                SUM(input_tokens) AS input_tokens,
                SUM(output_tokens) AS output_tokens,
                SUM(cached_tokens) AS cached_tokens,
                SUM(cost_total) AS total_cost
            FROM usage_events
            GROUP BY month, task_type, provider, model
            """
        )
        self._conn.commit()

    def get_monthly_total_cost(self, month: str) -> float:
        row = self._conn.execute(
            """
            SELECT COALESCE(SUM(total_cost), 0) AS total_cost
            FROM monthly_rollups
            WHERE month = ?
            """,
            (month,),
        ).fetchone()
        return float(row["total_cost"]) if row else 0.0

    def get_monthly_task_cost(self, month: str, task_type: str) -> float:
        row = self._conn.execute(
            """
            SELECT COALESCE(SUM(total_cost), 0) AS total_cost
            FROM monthly_rollups
            WHERE month = ? AND task_type = ?
            """,
            (month, task_type),
        ).fetchone()
        return float(row["total_cost"]) if row else 0.0

    def upsert_alert(self, alert: BudgetAlert) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO budget_alerts (
                id, month, scope_type, scope_value, limit_usd, current_usd,
                severity, status, triggered_at
            )
            VALUES (
                (
                    SELECT id FROM budget_alerts
                    WHERE month = ? AND scope_type = ? AND scope_value = ?
                    ORDER BY id ASC
                    LIMIT 1
                ),
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                alert.month,
                alert.scope_type,
                alert.scope_value,
                alert.month,
                alert.scope_type,
                alert.scope_value,
                alert.limit_usd,
                alert.current_usd,
                alert.severity,
                alert.status,
                alert.triggered_at,
            ),
        )
        self._conn.commit()

    def recent_usage(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT ts, task_type, provider, model, input_tokens, output_tokens,
                   cached_tokens, duration_ms, cost_total, status
            FROM usage_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def monthly_breakdown(self, month: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT month, task_type, provider, model, requests, input_tokens,
                   output_tokens, cached_tokens, total_cost
            FROM monthly_rollups
            WHERE month = ?
            ORDER BY total_cost DESC
            """,
            (month,),
        ).fetchall()
        return [dict(row) for row in rows]

    def open_alerts(self, month: str | None = None) -> list[dict[str, Any]]:
        if month:
            rows = self._conn.execute(
                """
                SELECT month, scope_type, scope_value, limit_usd, current_usd,
                       severity, status, triggered_at
                FROM budget_alerts
                WHERE month = ? AND status = 'open'
                ORDER BY triggered_at DESC
                """,
                (month,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT month, scope_type, scope_value, limit_usd, current_usd,
                       severity, status, triggered_at
                FROM budget_alerts
                WHERE status = 'open'
                ORDER BY triggered_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

