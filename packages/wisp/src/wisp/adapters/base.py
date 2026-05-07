"""Storage Protocol for Wisp.

The :class:`VaultAdapter` Protocol defines every read/write the rest of
the package needs against persistent state. Routes, evaluators, and
enrichments depend on this Protocol, never on a concrete adapter; the
SQLite implementation in v1 (and a future YAML implementation in v1.1+)
both satisfy it.

Discipline
----------
* All methods take a job by **integer id**. ``add_job`` is the one that
  hands the id back; everything else assumes the caller already has it.
* Methods that *change* a job's status (``mark_applied``, ``mark_skipped``,
  ``mark_pending``) are **idempotent**: calling them when the job is
  already in that state is a no-op for the timeline. They can still
  record a new ``decisions`` row when given a snapshot, because the
  user may legitimately re-confirm a click — but routing layer should
  guard against that if it isn't desired.
* The Protocol does not promise atomicity across multiple calls. The
  SQLite adapter wraps each method in its own transaction; callers that
  need cross-call atomicity should add a higher-level coordination point
  (none in v1).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import (
    DecisionAction,
    Enrichment,
    EnrichmentInput,
    Evaluation,
    EvaluationInput,
    Job,
    JobInput,
    JobListFilter,
    Signal,
    SignalSnapshot,
    TimelineEvent,
    TimelineEventInput,
)


@runtime_checkable
class VaultAdapter(Protocol):
    """The persistence surface the rest of Wisp talks to."""

    # ---- Jobs ---------------------------------------------------------------

    def list_jobs(self, filter: JobListFilter = "all") -> list[Job]:
        """Return jobs matching ``filter``, newest-first.

        ``filter`` of ``"pending"`` returns jobs whose latest composite
        evaluation has ``signal == "pending"`` regardless of
        ``jobs.status`` — that's how the UI surfaces "needs your attention".
        """

    def get_job(self, job_id: int) -> Job | None:
        """Return a single job row, or ``None`` if it doesn't exist."""

    def add_job(self, input: JobInput) -> Job:
        """Persist a new job and return the stored row (with assigned
        ``id``, ``created_at``, ``updated_at``).

        Also writes an opening ``Saved job`` timeline event in the same
        transaction.
        """

    def mark_applied(
        self,
        job_id: int,
        snapshot: SignalSnapshot | None = None,
    ) -> Job:
        """Set status to ``applied``. Idempotent.

        If ``snapshot`` is supplied, also writes a ``decisions`` row so
        the calibration table can compare AI advice vs the user's
        actual decision. Routes always pass one in production.
        """

    def mark_skipped(
        self,
        job_id: int,
        snapshot: SignalSnapshot | None = None,
        reason: str | None = None,
    ) -> Job:
        """Set status to ``skipped``. Idempotent.

        ``reason`` (if present) is stored in the ``Skipped`` timeline
        event's detail so it shows up on the cold-storage timeline.
        """

    def mark_pending(
        self,
        job_id: int,
        snapshot: SignalSnapshot | None = None,
    ) -> Job:
        """Move the job back to needs-decision state. Idempotent."""

    # ---- Timeline -----------------------------------------------------------

    def add_timeline_event(self, job_id: int, event: TimelineEventInput) -> TimelineEvent:
        """Append a free-form event. Used for notes, evaluator runs,
        and enrichment completion."""

    def list_timeline(self, job_id: int) -> list[TimelineEvent]:
        """Chronological events for a job, oldest-first."""

    def add_note(self, job_id: int, text: str) -> TimelineEvent:
        """Append a user-authored note as a timeline event with
        ``source='user'``. Convenience wrapper around
        ``add_timeline_event``."""

    # ---- Evaluations --------------------------------------------------------

    def add_evaluation(self, job_id: int, evaluation: EvaluationInput) -> Evaluation:
        """Persist one heuristic / ai / composite evaluation row."""

    def list_evaluations(self, job_id: int) -> list[Evaluation]:
        """All evaluations for a job, newest-first across all kinds."""

    def latest_evaluation(
        self,
        job_id: int,
        kind: str | None = None,
    ) -> Evaluation | None:
        """Most recent evaluation for a job. If ``kind`` is given, the
        most recent of that kind (used by the hot brief: latest composite)."""

    # ---- Decision checklist -------------------------------------------------

    def update_checklist(self, job_id: int, item_key: str, value: str) -> None:
        """Upsert one checklist answer. Replaces any prior answer for
        the same ``item_key``."""

    def get_checklist(self, job_id: int) -> dict[str, str]:
        """All current checklist answers as ``{item_key: value}``."""

    # ---- Decisions (calibration loop) --------------------------------------

    def add_decision(
        self,
        job_id: int,
        action: DecisionAction,
        snapshot: SignalSnapshot,
    ) -> None:
        """Record one Apply/Skip/Pending click for the calibration table.

        Usually called indirectly via ``mark_applied`` / ``mark_skipped``;
        exposed directly so re-confirmation flows can record without
        flipping ``jobs.status``."""

    # ---- Signal overrides --------------------------------------------------

    def add_override(
        self,
        job_id: int,
        original: Signal,
        user: Signal,
        reason: str | None = None,
    ) -> None:
        """Record a user "I disagree" override. Does not rewrite any
        evaluation row; original_signal stays in the audit trail."""

    # ---- Enrichments --------------------------------------------------------

    def add_enrichment(self, job_id: int, enrichment: EnrichmentInput) -> Enrichment:
        """Persist one enrichment provider result. Multiple results per
        provider per job are kept (history preserved across re-runs)."""

    def list_enrichments(self, job_id: int) -> list[Enrichment]:
        """All enrichment rows for a job, newest-first."""
