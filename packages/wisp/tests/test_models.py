"""Validation rules on the Pydantic models in ``wisp.models``.

Adapter tests exercise round-tripping; this file pins down the
constraints the models enforce on bad input.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wisp.models import (
    BRIEF_REASONS_MAX_ITEMS,
    BRIEF_RECOMMENDATION_MAX_LENGTH,
    EvaluationInput,
    Job,
    JobInput,
)

# ---- Salary monotonicity (#1) ---------------------------------------------


def test_jobinput_rejects_min_greater_than_max() -> None:
    with pytest.raises(ValidationError, match="salary_min .* cannot exceed salary_max"):
        JobInput(
            company="Linear",
            role="Sr Designer",
            salary_min=200_000,
            salary_max=150_000,
        )


def test_jobinput_allows_min_equal_to_max() -> None:
    """Single-point salary (e.g. fixed contract rate) is valid."""
    job = JobInput(
        company="Linear",
        role="Sr Designer",
        salary_min=150_000,
        salary_max=150_000,
    )
    assert job.salary_min == job.salary_max == 150_000


def test_jobinput_allows_either_or_both_bounds_unset() -> None:
    """The JD parser may extract one bound, or neither."""
    only_min = JobInput(company="A", role="x", salary_min=120_000)
    assert only_min.salary_max is None

    only_max = JobInput(company="A", role="x", salary_max=160_000)
    assert only_max.salary_min is None

    neither = JobInput(company="A", role="x")
    assert neither.salary_min is None and neither.salary_max is None


def test_job_rejects_min_greater_than_max_on_load() -> None:
    """Catch corruption coming back from a bad write — a future migration
    bug or a hand-edited DB shouldn't slip into the heuristic silently."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError, match="salary_min .* cannot exceed salary_max"):
        Job(
            id=1,
            company="Linear",
            role="Sr Designer",
            salary_min=200_000,
            salary_max=150_000,
            created_at=now,
            updated_at=now,
        )


# ---- Hot-brief length caps (#2) -------------------------------------------


def _valid_eval_kwargs() -> dict[str, object]:
    return dict(
        kind="composite",
        fit_score=0.7,
        confidence=0.6,
        signal="stretch",
        signal_label="Worth a closer look",
    )


def test_brief_recommendation_at_cap_is_accepted() -> None:
    """Exactly 140 chars must pass — the cap is inclusive."""
    text = "x" * BRIEF_RECOMMENDATION_MAX_LENGTH
    ev = EvaluationInput(brief_recommendation=text, **_valid_eval_kwargs())
    assert ev.brief_recommendation == text


def test_brief_recommendation_over_cap_is_rejected() -> None:
    """One char over → ValidationError, not a silent UX regression."""
    text = "x" * (BRIEF_RECOMMENDATION_MAX_LENGTH + 1)
    with pytest.raises(ValidationError):
        EvaluationInput(brief_recommendation=text, **_valid_eval_kwargs())


def test_brief_recommendation_can_be_none() -> None:
    """Heuristic-only paths may not generate one; the UI falls back to
    signal_label per the schema's nullable column."""
    ev = EvaluationInput(brief_recommendation=None, **_valid_eval_kwargs())
    assert ev.brief_recommendation is None


def test_brief_reasons_up_to_two_items_pass() -> None:
    ev = EvaluationInput(
        brief_reasons=["Skills match", "Salary below floor"],
        **_valid_eval_kwargs(),
    )
    assert len(ev.brief_reasons) == BRIEF_REASONS_MAX_ITEMS


def test_brief_reasons_three_items_rejected() -> None:
    """Plan said 1-2; a third bullet means the brief no longer fits the
    one-viewport contract."""
    with pytest.raises(ValidationError):
        EvaluationInput(
            brief_reasons=["a", "b", "c"],
            **_valid_eval_kwargs(),
        )


def test_brief_reasons_empty_list_accepted() -> None:
    """Heuristic-only paths can omit reasons; the UI must handle empty."""
    ev = EvaluationInput(brief_reasons=[], **_valid_eval_kwargs())
    assert ev.brief_reasons == []
