"""Validation rules on the Pydantic models in ``wisp.models``.

Adapter tests exercise round-tripping; this file pins down the
constraints the models enforce on bad input.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wisp.models import Job, JobInput

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
