"""Tests for :class:`wisp.adapters.SqliteVaultAdapter`.

Each test gets a fresh DB via the autouse ``WISP_DATA_DIR`` fixture.
We verify CRUD on every table, idempotence of state-changing methods,
JSON round-trips, and Protocol conformance.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from wisp import db
from wisp.adapters import SqliteVaultAdapter, VaultAdapter
from wisp.models import (
    EnrichmentInput,
    EvaluationInput,
    JobInput,
    JobUpdate,
    SignalSnapshot,
    TimelineEventInput,
)


@pytest.fixture
def adapter(tmp_path: Path) -> Iterator[SqliteVaultAdapter]:
    conn = db.init_db(tmp_path / "x.db")
    a = SqliteVaultAdapter(conn)
    try:
        yield a
    finally:
        a.close()


@pytest.fixture
def job_id(adapter: SqliteVaultAdapter) -> int:
    job = adapter.add_job(
        JobInput(company="Linear", role="Senior Product Designer", location="Remote")
    )
    return job.id


# ---- Conformance -----------------------------------------------------------


def test_adapter_satisfies_protocol(adapter: SqliteVaultAdapter) -> None:
    """Runtime-check the Protocol so a missing method shows up here, not
    in a route handler at request time."""
    assert isinstance(adapter, VaultAdapter)


# ---- Jobs ------------------------------------------------------------------


def test_add_and_get_job(adapter: SqliteVaultAdapter) -> None:
    created = adapter.add_job(
        JobInput(
            company="Linear",
            role="Senior Product Designer",
            location="Remote",
            salary_min=130_000,
            salary_max=160_000,
            salary_currency="usd",
        )
    )
    assert created.id > 0
    assert created.status == "decide"

    fetched = adapter.get_job(created.id)
    assert fetched is not None
    assert fetched.company == "Linear"
    assert fetched.salary_min == 130_000
    assert fetched.salary_currency == "usd"


def test_get_job_returns_none_for_missing(adapter: SqliteVaultAdapter) -> None:
    assert adapter.get_job(999_999) is None


def test_add_job_writes_opening_timeline_event(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    timeline = adapter.list_timeline(job_id)
    assert len(timeline) == 1
    assert timeline[0].label == "Saved job"
    assert timeline[0].source == "user"


def test_update_job_patches_only_provided_fields(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    """Fields not in the patch payload stay untouched."""
    before = adapter.get_job(job_id)
    assert before is not None and before.role == "Senior Product Designer"

    after = adapter.update_job(
        job_id,
        JobUpdate(role="Staff Product Designer", salary_min=160_000, salary_max=200_000),
    )
    # Patched fields changed:
    assert after.role == "Staff Product Designer"
    assert after.salary_min == 160_000
    assert after.salary_max == 200_000
    # Untouched fields preserved:
    assert after.company == before.company
    assert after.location == before.location


def test_update_job_explicit_none_clears_field(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    """Setting a field to None clears it (different from not passing it)."""
    adapter.update_job(job_id, JobUpdate(salary_min=140_000, salary_max=170_000))
    cleared = adapter.update_job(job_id, JobUpdate(salary_min=None))
    assert cleared.salary_min is None
    assert cleared.salary_max == 170_000  # untouched


def test_update_job_appends_timeline_event(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.update_job(job_id, JobUpdate(role="Staff Product Designer"))
    last = adapter.list_timeline(job_id)[-1]
    assert last.label == "Updated job details"
    assert last.detail == "role"
    assert last.source == "user"


def test_update_job_lists_all_changed_fields_alphabetically(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.update_job(
        job_id,
        JobUpdate(role="Staff", company="Vercel", location="Remote"),
    )
    last = adapter.list_timeline(job_id)[-1]
    assert last.detail == "company, location, role"


def test_update_job_empty_patch_is_a_noop(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    """No fields set → no UPDATE, no timeline event."""
    timeline_before = adapter.list_timeline(job_id)
    job_before = adapter.get_job(job_id)
    assert job_before is not None

    after = adapter.update_job(job_id, JobUpdate())

    assert after.updated_at == job_before.updated_at  # untouched
    assert adapter.list_timeline(job_id) == timeline_before


def test_update_job_rejects_partial_patch_violating_salary_monotonicity(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    """Setting salary_min higher than the existing salary_max must be
    rejected — we validate the MERGED row, not just the patch."""
    adapter.update_job(job_id, JobUpdate(salary_min=100_000, salary_max=120_000))
    with pytest.raises(ValidationError, match="salary_min .* cannot exceed salary_max"):
        adapter.update_job(job_id, JobUpdate(salary_min=200_000))


def test_update_job_on_missing_raises(adapter: SqliteVaultAdapter) -> None:
    with pytest.raises(KeyError, match="999"):
        adapter.update_job(999, JobUpdate(role="x"))


def test_list_jobs_all_and_status_filters(adapter: SqliteVaultAdapter) -> None:
    a = adapter.add_job(JobInput(company="A", role="x"))
    b = adapter.add_job(JobInput(company="B", role="x"))
    c = adapter.add_job(JobInput(company="C", role="x"))

    adapter.mark_applied(b.id)
    adapter.mark_skipped(c.id)

    all_jobs = adapter.list_jobs("all")
    assert {j.id for j in all_jobs} == {a.id, b.id, c.id}

    assert {j.id for j in adapter.list_jobs("decide")} == {a.id}
    assert {j.id for j in adapter.list_jobs("applied")} == {b.id}
    assert {j.id for j in adapter.list_jobs("skipped")} == {c.id}


def test_list_jobs_pending_uses_latest_composite(
    adapter: SqliteVaultAdapter,
) -> None:
    """The 'pending' filter looks at the latest composite evaluation,
    not jobs.status. A previous composite that was not 'pending' must
    not keep the job in the pending bucket."""
    a = adapter.add_job(JobInput(company="A", role="x"))
    b = adapter.add_job(JobInput(company="B", role="x"))

    # A: latest composite says yes; not pending
    adapter.add_evaluation(
        a.id,
        EvaluationInput(
            kind="composite", fit_score=0.9, confidence=0.9,
            signal="yes", signal_label="Worth pursuing",
        ),
    )
    # B: first composite says yes, then a newer one says pending
    adapter.add_evaluation(
        b.id,
        EvaluationInput(
            kind="composite", fit_score=0.8, confidence=0.7,
            signal="yes", signal_label="Worth pursuing",
        ),
    )
    adapter.add_evaluation(
        b.id,
        EvaluationInput(
            kind="composite", fit_score=0.5, confidence=0.2,
            signal="pending", signal_label="Need more info",
        ),
    )

    pending = adapter.list_jobs("pending")
    assert {j.id for j in pending} == {b.id}


# ---- mark_* idempotence ----------------------------------------------------


def test_mark_applied_appends_timeline_and_decision(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    snap = SignalSnapshot(
        signal="yes", signal_label="Worth pursuing",
        fit_score=0.85, confidence=0.8,
    )
    adapter.mark_applied(job_id, snap)

    job = adapter.get_job(job_id)
    assert job is not None and job.status == "applied"

    # Saved job + Marked as Applied
    timeline = adapter.list_timeline(job_id)
    assert [e.label for e in timeline] == ["Saved job", "Marked as Applied"]

    # One decision row recorded
    rows = adapter.connection.execute(
        "SELECT action, signal_at_time, fit_score_at_time FROM decisions"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["action"] == "apply"
    assert rows[0]["signal_at_time"] == "yes"
    assert rows[0]["fit_score_at_time"] == 0.85


def test_mark_applied_is_idempotent(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    snap = SignalSnapshot(
        signal="yes", signal_label="Worth pursuing",
        fit_score=0.85, confidence=0.8,
    )
    adapter.mark_applied(job_id, snap)
    adapter.mark_applied(job_id, snap)  # no-op
    adapter.mark_applied(job_id, snap)  # no-op

    timeline = adapter.list_timeline(job_id)
    assert [e.label for e in timeline] == ["Saved job", "Marked as Applied"]

    decisions = adapter.connection.execute(
        "SELECT COUNT(*) FROM decisions"
    ).fetchone()[0]
    assert decisions == 1, "re-applying must not duplicate decisions"


def test_mark_applied_without_snapshot_skips_decision_row(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.mark_applied(job_id)
    decisions = adapter.connection.execute(
        "SELECT COUNT(*) FROM decisions"
    ).fetchone()[0]
    assert decisions == 0


def test_mark_skipped_records_reason_in_timeline(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.mark_skipped(job_id, reason="Salary too low")
    timeline = adapter.list_timeline(job_id)
    assert timeline[-1].label == "Marked as Skipped"
    assert timeline[-1].detail == "Salary too low"


def test_mark_pending_returns_to_decide(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.mark_applied(job_id)
    adapter.mark_pending(job_id)
    job = adapter.get_job(job_id)
    assert job is not None and job.status == "decide"


def test_mark_on_missing_job_raises(adapter: SqliteVaultAdapter) -> None:
    with pytest.raises(KeyError, match="999"):
        adapter.mark_applied(999)


# ---- Evaluations -----------------------------------------------------------


def test_add_evaluation_round_trips_json_columns(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    ev = adapter.add_evaluation(
        job_id,
        EvaluationInput(
            kind="composite",
            fit_score=0.78,
            confidence=0.65,
            signal="stretch",
            signal_label="Worth a closer look",
            brief_recommendation="I'd lean apply but the bar is high.",
            brief_reasons=["Skills match", "Salary below floor"],
            summary="Linear's design culture aligns closely.",
            strengths=["Design systems experience", "Remote-first culture"],
            gaps=["No mobile work in portfolio"],
            concerns=["High competition"],
            cautions=["Tailor cover letter"],
            recommendation="Apply with a focused portfolio.",
            evidence=[{"field": "skills", "snippet": "Figma · Linear"}],
        ),
    )
    fetched = adapter.list_evaluations(job_id)[0]
    assert fetched.id == ev.id
    assert fetched.brief_reasons == ["Skills match", "Salary below floor"]
    assert fetched.strengths == ["Design systems experience", "Remote-first culture"]
    assert fetched.evidence == [{"field": "skills", "snippet": "Figma · Linear"}]


def test_list_evaluations_newest_first(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    e1 = adapter.add_evaluation(
        job_id,
        EvaluationInput(
            kind="heuristic", fit_score=0.5, confidence=0.4,
            signal="maybe", signal_label="Mixed signals",
        ),
    )
    e2 = adapter.add_evaluation(
        job_id,
        EvaluationInput(
            kind="ai", fit_score=0.7, confidence=0.8,
            signal="yes", signal_label="Worth pursuing",
        ),
    )
    rows = adapter.list_evaluations(job_id)
    assert [r.id for r in rows] == [e2.id, e1.id]


def test_latest_evaluation_filters_by_kind(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    h1 = adapter.add_evaluation(
        job_id,
        EvaluationInput(
            kind="heuristic", fit_score=0.4, confidence=0.4,
            signal="maybe", signal_label="Mixed signals",
        ),
    )
    a1 = adapter.add_evaluation(
        job_id,
        EvaluationInput(
            kind="ai", fit_score=0.7, confidence=0.8,
            signal="yes", signal_label="Worth pursuing",
        ),
    )
    h2 = adapter.add_evaluation(
        job_id,
        EvaluationInput(
            kind="heuristic", fit_score=0.6, confidence=0.5,
            signal="stretch", signal_label="Worth a closer look",
        ),
    )

    latest_any = adapter.latest_evaluation(job_id)
    assert latest_any is not None and latest_any.id == h2.id

    latest_h = adapter.latest_evaluation(job_id, kind="heuristic")
    assert latest_h is not None and latest_h.id == h2.id

    latest_a = adapter.latest_evaluation(job_id, kind="ai")
    assert latest_a is not None and latest_a.id == a1.id

    assert adapter.latest_evaluation(job_id, kind="composite") is None
    assert h1.id != h2.id  # silence "h1 unused"


# ---- Timeline + notes ------------------------------------------------------


def test_add_note_creates_user_sourced_event(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.add_note(job_id, "Followed up via email.")
    last = adapter.list_timeline(job_id)[-1]
    assert last.label == "Note"
    assert last.detail == "Followed up via email."
    assert last.source == "user"


def test_add_timeline_event_accepts_open_source_tags(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    """timeline.source CHECK was dropped — new tags work."""
    adapter.add_timeline_event(
        job_id,
        TimelineEventInput(label="Auto re-eval", detail=None, source="cron"),
    )
    last = adapter.list_timeline(job_id)[-1]
    assert last.source == "cron"


# ---- Checklist -------------------------------------------------------------


def test_update_checklist_upserts(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.update_checklist(job_id, "fit", "yes")
    adapter.update_checklist(job_id, "qualified", "maybe")
    assert adapter.get_checklist(job_id) == {"fit": "yes", "qualified": "maybe"}

    # Re-update replaces, not appends
    adapter.update_checklist(job_id, "fit", "no")
    assert adapter.get_checklist(job_id) == {"fit": "no", "qualified": "maybe"}


def test_checklist_value_can_be_arbitrary_string(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    """value CHECK was dropped — a 1-5 scale or custom keys are allowed."""
    adapter.update_checklist(job_id, "fit", "4")
    adapter.update_checklist(job_id, "remote_friendly", "definitely")
    assert adapter.get_checklist(job_id) == {
        "fit": "4",
        "remote_friendly": "definitely",
    }


# ---- Decisions / overrides -------------------------------------------------


def test_add_decision_standalone(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    snap = SignalSnapshot(
        signal="pending", signal_label="Need more info",
        fit_score=0.5, confidence=0.2,
    )
    adapter.add_decision(job_id, "pending", snap)
    rows = adapter.connection.execute(
        "SELECT action, signal_at_time FROM decisions"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["action"] == "pending"


def test_add_override_records_both_signals(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.add_override(
        job_id, original="yes", user="stretch", reason="Salary lower than I'd like"
    )
    rows = adapter.connection.execute(
        "SELECT original_signal, user_signal, reason FROM signal_overrides"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["original_signal"] == "yes"
    assert rows[0]["user_signal"] == "stretch"
    assert rows[0]["reason"] == "Salary lower than I'd like"


# ---- Enrichments -----------------------------------------------------------


def test_add_enrichment_with_dict_result(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    e = adapter.add_enrichment(
        job_id,
        EnrichmentInput(
            provider_key="manual_company_notes",
            source="user",
            result={"notes": "Founders are ex-Stripe."},
        ),
    )
    assert e.result == {"notes": "Founders are ex-Stripe."}


def test_add_enrichment_with_list_result(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    e = adapter.add_enrichment(
        job_id,
        EnrichmentInput(
            provider_key="online_comments",
            source="web",
            result=[{"site": "HN", "summary": "Reviews are positive."}],
        ),
    )
    assert isinstance(e.result, list)
    assert e.result[0]["site"] == "HN"


def test_add_enrichment_with_null_result_round_trips(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    e = adapter.add_enrichment(
        job_id,
        EnrichmentInput(
            provider_key="glassdoor",
            source="api",
            status="pending",
            result=None,
        ),
    )
    assert e.result is None
    assert e.status == "pending"


def test_list_enrichments_keeps_history(
    adapter: SqliteVaultAdapter, job_id: int
) -> None:
    adapter.add_enrichment(
        job_id,
        EnrichmentInput(provider_key="manual_company_notes", source="user",
                        result={"notes": "v1"}),
    )
    adapter.add_enrichment(
        job_id,
        EnrichmentInput(provider_key="manual_company_notes", source="user",
                        result={"notes": "v2"}),
    )
    items = adapter.list_enrichments(job_id)
    assert len(items) == 2
    # Newest first
    assert items[0].result == {"notes": "v2"}
    assert items[1].result == {"notes": "v1"}


# ---- Cascading deletes -----------------------------------------------------


def test_deleting_a_job_cascades_through_adapter_tables(
    adapter: SqliteVaultAdapter,
) -> None:
    """Belt-and-braces: even after the adapter writes evaluations,
    timeline, decisions, overrides, enrichments, deleting the job
    removes all of them via the FK cascade."""
    job = adapter.add_job(JobInput(company="Linear", role="x"))
    adapter.mark_applied(
        job.id,
        SignalSnapshot(signal="yes", fit_score=0.8, confidence=0.7),
    )
    adapter.add_evaluation(
        job.id,
        EvaluationInput(
            kind="heuristic", fit_score=0.5, confidence=0.4,
            signal="maybe", signal_label="Mixed signals",
        ),
    )
    adapter.add_override(job.id, original="yes", user="stretch")
    adapter.add_enrichment(
        job.id,
        EnrichmentInput(provider_key="manual_company_notes", source="user",
                        result={"notes": "x"}),
    )
    adapter.update_checklist(job.id, "fit", "yes")

    adapter.connection.execute("DELETE FROM jobs WHERE id = ?", (job.id,))
    adapter.connection.commit()

    for table in (
        "timeline_events", "evaluations", "decisions",
        "signal_overrides", "enrichments", "decision_checklist",
    ):
        n = adapter.connection.execute(
            f"SELECT COUNT(*) FROM {table} WHERE job_id = ?", (job.id,)
        ).fetchone()[0]
        assert n == 0, f"{table} still has rows for job {job.id}"


