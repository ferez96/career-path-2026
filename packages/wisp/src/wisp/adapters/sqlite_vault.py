"""SQLite-backed implementation of :class:`VaultAdapter`.

All writes go through parameterized queries (no f-strings or string
concat). State-changing ``mark_*`` methods are no-ops when the job is
already in the target state. JSON-encoded columns round-trip through
:mod:`json` at the persistence boundary so callers never see raw strings.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from .. import db
from ..models import (
    DecisionAction,
    Enrichment,
    EnrichmentInput,
    Evaluation,
    EvaluationInput,
    Job,
    JobInput,
    JobListFilter,
    JobUpdate,
    Signal,
    SignalSnapshot,
    TimelineEvent,
    TimelineEventInput,
)

# ---- helpers --------------------------------------------------------------


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    # sqlite3.Row iterates VALUES (not keys); .keys() is the documented way
    # to get column names, hence the noqa.
    return {k: row[k] for k in row.keys()}  # noqa: SIM118


def _json_or_default(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    return json.loads(value)


def _row_to_job(row: sqlite3.Row) -> Job:
    return Job.model_validate(_row_to_dict(row))


def _row_to_evaluation(row: sqlite3.Row) -> Evaluation:
    raw = _row_to_dict(row)
    raw["brief_reasons"] = _json_or_default(raw.pop("brief_reasons_json", None), [])
    raw["strengths"] = _json_or_default(raw.pop("strengths_json", None), [])
    raw["gaps"] = _json_or_default(raw.pop("gaps_json", None), [])
    raw["concerns"] = _json_or_default(raw.pop("concerns_json", None), [])
    raw["cautions"] = _json_or_default(raw.pop("cautions_json", None), [])
    raw["evidence"] = _json_or_default(raw.pop("evidence_json", None), [])
    return Evaluation.model_validate(raw)


def _row_to_timeline(row: sqlite3.Row) -> TimelineEvent:
    return TimelineEvent.model_validate(_row_to_dict(row))


def _row_to_enrichment(row: sqlite3.Row) -> Enrichment:
    raw = _row_to_dict(row)
    raw["result"] = _json_or_default(raw.pop("result_json", None), None)
    return Enrichment.model_validate(raw)


# ---- adapter --------------------------------------------------------------


class SqliteVaultAdapter:
    """:class:`~wisp.adapters.VaultAdapter` backed by SQLite.

    The adapter owns its connection. Callers obtain one via
    :meth:`open` (which also runs migrations) or pass an already-prepared
    connection — useful for tests that share a temp DB across operations.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    @classmethod
    def open(cls) -> SqliteVaultAdapter:
        """Open the user's DB at :func:`config.db_path`, applying any
        pending migrations."""
        return cls(db.init_db())

    def close(self) -> None:
        self._conn.close()

    @property
    def connection(self) -> sqlite3.Connection:
        """Escape hatch for tests / one-off queries. Avoid in app code."""
        return self._conn

    # ---- Jobs ---------------------------------------------------------------

    def list_jobs(self, filter: JobListFilter = "all") -> list[Job]:
        cur = self._conn.cursor()
        if filter == "pending":
            # Latest composite per job; surface those whose signal is 'pending'
            # regardless of jobs.status. Uses correlated subquery so we don't
            # need window functions (works on older SQLite).
            cur.execute(
                """
                SELECT j.* FROM jobs j
                WHERE EXISTS (
                  SELECT 1 FROM evaluations e
                  WHERE e.job_id = j.id
                    AND e.kind = 'composite'
                    AND e.signal = 'pending'
                    AND e.evaluated_at = (
                      SELECT MAX(e2.evaluated_at) FROM evaluations e2
                      WHERE e2.job_id = j.id AND e2.kind = 'composite'
                    )
                )
                ORDER BY j.created_at DESC
                """
            )
        elif filter == "all":
            cur.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        else:
            cur.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC",
                (filter,),
            )
        return [_row_to_job(row) for row in cur.fetchall()]

    def get_job(self, job_id: int) -> Job | None:
        row = self._conn.execute(
            "SELECT * FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return _row_to_job(row) if row else None

    def add_job(self, input: JobInput) -> Job:
        cur = self._conn.execute(
            """
            INSERT INTO jobs (
                company, role, location, work_type, employment_type,
                salary_range, salary_min, salary_max, salary_currency,
                source, source_url, raw_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                input.company,
                input.role,
                input.location,
                input.work_type,
                input.employment_type,
                input.salary_range,
                input.salary_min,
                input.salary_max,
                input.salary_currency,
                input.source,
                input.source_url,
                input.raw_content,
            ),
        )
        job_id = cur.lastrowid
        assert job_id is not None  # sqlite3 always returns one for INSERT
        self._conn.execute(
            "INSERT INTO timeline_events (job_id, label, source) VALUES (?, ?, ?)",
            (job_id, "Saved job", "user"),
        )
        self._conn.commit()
        result = self.get_job(job_id)
        assert result is not None  # we just inserted it
        return result

    # Whitelist of columns ``update_job`` is allowed to write. Built from
    # JobUpdate's fields rather than user input, so the dynamic SET clause
    # below is safe from SQL injection by construction.
    _UPDATABLE_JOB_COLUMNS: frozenset[str] = frozenset(JobUpdate.model_fields.keys())

    def update_job(self, job_id: int, update: JobUpdate) -> Job:
        existing = self.get_job(job_id)
        if existing is None:
            raise KeyError(f"Job {job_id!r} does not exist")

        # Only fields the caller explicitly set on the patch
        patch = update.model_dump(exclude_unset=True)
        if not patch:
            return existing

        # Defensive: filter to known column names so a stray field on a
        # tolerant model can't ever leak into SQL.
        patch = {k: v for k, v in patch.items() if k in self._UPDATABLE_JOB_COLUMNS}
        if not patch:
            return existing

        # Validate the merged result against Job's constraints (salary
        # monotonicity, status enum, score ranges via field types) before
        # writing. Rejects e.g. setting only salary_min higher than the
        # untouched salary_max.
        merged = existing.model_dump()
        merged.update(patch)
        Job.model_validate(merged)

        set_cols = ", ".join(f"{col} = ?" for col in patch)
        values: list[object] = list(patch.values())
        self._conn.execute(
            f"UPDATE jobs SET {set_cols}, "
            f"updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') WHERE id = ?",
            (*values, job_id),
        )
        self._conn.execute(
            "INSERT INTO timeline_events (job_id, label, detail, source) "
            "VALUES (?, ?, ?, ?)",
            (
                job_id,
                "Updated job details",
                ", ".join(sorted(patch.keys())),
                "user",
            ),
        )
        self._conn.commit()

        updated = self.get_job(job_id)
        assert updated is not None
        return updated

    def _set_status(
        self,
        job_id: int,
        target_status: str,
        timeline_label: str,
        decision_action: DecisionAction,
        snapshot: SignalSnapshot | None,
        reason: str | None = None,
    ) -> Job:
        """Shared idempotent transition logic for ``mark_*`` methods.

        If the job is already in ``target_status``, return it unchanged.
        Otherwise update status, append a timeline event, and (when a
        snapshot is supplied) record a ``decisions`` row.
        """
        existing = self.get_job(job_id)
        if existing is None:
            raise KeyError(f"Job {job_id!r} does not exist")
        if existing.status == target_status:
            return existing
        self._conn.execute(
            "UPDATE jobs SET status = ?, "
            "updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') WHERE id = ?",
            (target_status, job_id),
        )
        self._conn.execute(
            "INSERT INTO timeline_events (job_id, label, detail, source) "
            "VALUES (?, ?, ?, ?)",
            (job_id, timeline_label, reason, "user"),
        )
        if snapshot is not None:
            self._insert_decision(job_id, decision_action, snapshot)
        self._conn.commit()
        updated = self.get_job(job_id)
        assert updated is not None
        return updated

    def mark_applied(
        self,
        job_id: int,
        snapshot: SignalSnapshot | None = None,
    ) -> Job:
        return self._set_status(
            job_id, "applied", "Marked as Applied", "apply", snapshot
        )

    def mark_skipped(
        self,
        job_id: int,
        snapshot: SignalSnapshot | None = None,
        reason: str | None = None,
    ) -> Job:
        return self._set_status(
            job_id, "skipped", "Marked as Skipped", "skip", snapshot, reason
        )

    def mark_pending(
        self,
        job_id: int,
        snapshot: SignalSnapshot | None = None,
    ) -> Job:
        return self._set_status(
            job_id, "decide", "Marked as Pending", "pending", snapshot
        )

    # ---- Timeline -----------------------------------------------------------

    def add_timeline_event(
        self, job_id: int, event: TimelineEventInput
    ) -> TimelineEvent:
        cur = self._conn.execute(
            "INSERT INTO timeline_events (job_id, label, detail, source, state) "
            "VALUES (?, ?, ?, ?, ?)",
            (job_id, event.label, event.detail, event.source, event.state),
        )
        event_id = cur.lastrowid
        assert event_id is not None
        self._conn.commit()
        row = self._conn.execute(
            "SELECT * FROM timeline_events WHERE id = ?", (event_id,)
        ).fetchone()
        return _row_to_timeline(row)

    def list_timeline(self, job_id: int) -> list[TimelineEvent]:
        rows = self._conn.execute(
            "SELECT * FROM timeline_events WHERE job_id = ? "
            "ORDER BY occurred_at ASC, id ASC",
            (job_id,),
        ).fetchall()
        return [_row_to_timeline(r) for r in rows]

    def add_note(self, job_id: int, text: str) -> TimelineEvent:
        return self.add_timeline_event(
            job_id,
            TimelineEventInput(label="Note", detail=text, source="user"),
        )

    # ---- Evaluations --------------------------------------------------------

    def add_evaluation(
        self, job_id: int, evaluation: EvaluationInput
    ) -> Evaluation:
        cur = self._conn.execute(
            """
            INSERT INTO evaluations (
                job_id, kind, fit_score, confidence, signal, signal_label,
                brief_recommendation, brief_reasons_json,
                summary, strengths_json, gaps_json, concerns_json,
                cautions_json, recommendation, evidence_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                evaluation.kind,
                evaluation.fit_score,
                evaluation.confidence,
                evaluation.signal,
                evaluation.signal_label,
                evaluation.brief_recommendation,
                json.dumps(evaluation.brief_reasons),
                evaluation.summary,
                json.dumps(evaluation.strengths),
                json.dumps(evaluation.gaps),
                json.dumps(evaluation.concerns),
                json.dumps(evaluation.cautions),
                evaluation.recommendation,
                json.dumps(evaluation.evidence),
            ),
        )
        eval_id = cur.lastrowid
        assert eval_id is not None
        self._conn.commit()
        row = self._conn.execute(
            "SELECT * FROM evaluations WHERE id = ?", (eval_id,)
        ).fetchone()
        return _row_to_evaluation(row)

    def list_evaluations(self, job_id: int) -> list[Evaluation]:
        rows = self._conn.execute(
            "SELECT * FROM evaluations WHERE job_id = ? "
            "ORDER BY evaluated_at DESC, id DESC",
            (job_id,),
        ).fetchall()
        return [_row_to_evaluation(r) for r in rows]

    def latest_evaluation(
        self,
        job_id: int,
        kind: str | None = None,
    ) -> Evaluation | None:
        if kind is None:
            row = self._conn.execute(
                "SELECT * FROM evaluations WHERE job_id = ? "
                "ORDER BY evaluated_at DESC, id DESC LIMIT 1",
                (job_id,),
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT * FROM evaluations WHERE job_id = ? AND kind = ? "
                "ORDER BY evaluated_at DESC, id DESC LIMIT 1",
                (job_id, kind),
            ).fetchone()
        return _row_to_evaluation(row) if row else None

    # ---- Decision checklist -------------------------------------------------

    def update_checklist(self, job_id: int, item_key: str, value: str) -> None:
        # SQLite UPSERT: replace any prior answer for the same (job_id, item_key).
        self._conn.execute(
            """
            INSERT INTO decision_checklist (job_id, item_key, value)
            VALUES (?, ?, ?)
            ON CONFLICT (job_id, item_key) DO UPDATE
              SET value = excluded.value,
                  updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            """,
            (job_id, item_key, value),
        )
        self._conn.commit()

    def get_checklist(self, job_id: int) -> dict[str, str]:
        rows = self._conn.execute(
            "SELECT item_key, value FROM decision_checklist WHERE job_id = ?",
            (job_id,),
        ).fetchall()
        return {row["item_key"]: row["value"] for row in rows}

    # ---- Decisions ----------------------------------------------------------

    def _insert_decision(
        self,
        job_id: int,
        action: DecisionAction,
        snapshot: SignalSnapshot,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO decisions (
                job_id, action, signal_at_time, signal_label_at_time,
                fit_score_at_time, confidence_at_time
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                action,
                snapshot.signal,
                snapshot.signal_label,
                snapshot.fit_score,
                snapshot.confidence,
            ),
        )

    def add_decision(
        self,
        job_id: int,
        action: DecisionAction,
        snapshot: SignalSnapshot,
    ) -> None:
        self._insert_decision(job_id, action, snapshot)
        self._conn.commit()

    # ---- Signal overrides --------------------------------------------------

    def add_override(
        self,
        job_id: int,
        original: Signal,
        user: Signal,
        reason: str | None = None,
    ) -> None:
        self._conn.execute(
            "INSERT INTO signal_overrides (job_id, original_signal, user_signal, reason) "
            "VALUES (?, ?, ?, ?)",
            (job_id, original, user, reason),
        )
        self._conn.commit()

    # ---- Enrichments --------------------------------------------------------

    def add_enrichment(
        self, job_id: int, enrichment: EnrichmentInput
    ) -> Enrichment:
        result_json = (
            json.dumps(enrichment.result) if enrichment.result is not None else None
        )
        cur = self._conn.execute(
            """
            INSERT INTO enrichments (
                job_id, provider_key, status, result_json, source
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                job_id,
                enrichment.provider_key,
                enrichment.status,
                result_json,
                enrichment.source,
            ),
        )
        enr_id = cur.lastrowid
        assert enr_id is not None
        self._conn.commit()
        row = self._conn.execute(
            "SELECT * FROM enrichments WHERE id = ?", (enr_id,)
        ).fetchone()
        return _row_to_enrichment(row)

    def list_enrichments(self, job_id: int) -> list[Enrichment]:
        rows = self._conn.execute(
            "SELECT * FROM enrichments WHERE job_id = ? "
            "ORDER BY created_at DESC, id DESC",
            (job_id,),
        ).fetchall()
        return [_row_to_enrichment(r) for r in rows]
