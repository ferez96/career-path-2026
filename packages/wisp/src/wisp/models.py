"""Domain models that flow through the :class:`VaultAdapter` Protocol.

These mirror the schema in ``001_init.sql`` but live independently of the
DB layer so we can swap adapters (SQLite v1, Yaml in v1.1+) without
moving Python types around. Defaults align with the schema's
NULL-as-empty convention.

JSON-encoded list/object columns (``brief_reasons_json``, ``strengths_json``,
``evidence_json``, ``result_json``) round-trip through these models as
typed Python lists/dicts. The adapter is responsible for the JSON
serialization at the persistence boundary.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---- Literal types ---------------------------------------------------------

# Mirrors the kept ``CHECK`` constraints in 001_init.sql. Adding values
# here also requires widening the DB CHECK; see db.py module docstring.

JobStatus = Literal["saved", "decide", "applied", "skipped"]
"""Status enum carried by :class:`Job`. Drives the list filter and the
overview tiles. Schema-enforced."""

JobListFilter = Literal["all", "decide", "applied", "skipped", "pending"]
"""Adapter-side filter for ``list_jobs``. ``pending`` is derived: jobs whose
latest composite evaluation has ``signal == 'pending'`` regardless of
``jobs.status``."""

EvaluationKind = Literal["heuristic", "ai", "composite"]
"""Each evaluation row tags itself; ``composite.py`` merges heuristic + ai
into a composite row, all three persist for audit."""

Signal = Literal["yes", "stretch", "maybe", "no", "pending"]
"""Composite output state. ``pending`` means low confidence / disagreement
between heuristic and AI; the UI surfaces it as 'Need more info'."""

DecisionAction = Literal["apply", "skip", "pending", "reopen"]
"""One row per Apply/Skip/Pending click. Powers /overview calibration."""


# ---- Helpers ---------------------------------------------------------------

# All models tolerate unknown fields so an older Wisp can read rows
# written by a newer one without crashing. Same convention as config.py.
_TOLERANT = ConfigDict(extra="ignore")

# Constrained scores: validated at model boundaries to match the DB CHECK.
Score = Annotated[float, Field(ge=0.0, le=1.0)]

# Hot-brief length cap. The plan pinned the default detail view to one
# viewport (≤1280×800); the verdict line and its 1-2 reasons are the only
# generated content rendered above the fold. Exceeding either is a UX
# regression, not just a style nit, so enforce at the model boundary.
BRIEF_RECOMMENDATION_MAX_LENGTH = 140
BRIEF_REASONS_MAX_ITEMS = 2

BriefRecommendation = Annotated[str, Field(max_length=BRIEF_RECOMMENDATION_MAX_LENGTH)]
BriefReasons = Annotated[
    list[str],
    Field(max_length=BRIEF_REASONS_MAX_ITEMS),
]


def _check_salary_monotonic(
    salary_min: int | None,
    salary_max: int | None,
) -> None:
    """Reject `min > max` when both are set. Either side may be ``None``
    (the JD parser couldn't extract that bound) and that's fine."""
    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        raise ValueError(
            f"salary_min ({salary_min}) cannot exceed salary_max ({salary_max})"
        )


# ---- Inputs (forms / evaluator emissions) ---------------------------------


class JobInput(BaseModel):
    """Fields the "Add a job" form posts — what we need to persist a row.

    The handler runs JD normalize → fills as many of these as it can; the
    user can edit any of them on the detail page before evaluation runs.
    Only ``company`` and ``role`` are strictly required.
    """

    model_config = _TOLERANT

    company: str
    role: str
    location: str | None = None
    work_type: str | None = None
    employment_type: str | None = None
    salary_range: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "USD"
    source: str | None = None
    source_url: str | None = None
    raw_content: str | None = None

    @model_validator(mode="after")
    def _validate_salary_range(self) -> JobInput:
        _check_salary_monotonic(self.salary_min, self.salary_max)
        return self


class EvaluationInput(BaseModel):
    """What an evaluator (heuristic, AI, or composite merger) emits.

    Persisted as one row per call; the adapter assigns ``id`` and
    ``evaluated_at``. ``brief_recommendation`` is optional — heuristic-only
    paths may leave it ``None`` and the UI falls back to ``signal_label``.
    """

    model_config = _TOLERANT

    kind: EvaluationKind
    fit_score: Score
    confidence: Score
    signal: Signal
    signal_label: str
    brief_recommendation: BriefRecommendation | None = None
    brief_reasons: BriefReasons = Field(default_factory=list)
    summary: str | None = None
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)


class TimelineEventInput(BaseModel):
    """One event to append to a job's timeline."""

    model_config = _TOLERANT

    label: str
    detail: str | None = None
    source: str  # 'user' | 'heuristic' | 'ai' | 'inbox' | 'cron' | ...
    state: str = "done"  # 'done' | 'current' | 'pending'


class EnrichmentInput(BaseModel):
    """One result from an enrichment provider (manual notes today;
    web-search / Glassdoor / Ollama / etc. as v1.1)."""

    model_config = _TOLERANT

    provider_key: str
    status: str = "done"  # 'pending' | 'running' | 'done' | 'failed'
    source: str  # 'user' | 'ai' | 'web' | 'api' | 'local' | ...
    result: dict[str, Any] | list[Any] | None = None


class SignalSnapshot(BaseModel):
    """Signal + score-at-time, recorded with an Apply/Skip/Pending click.

    Lets ``/overview`` ask "of jobs I labelled Strong fit, what fraction
    did the user actually apply?" without needing a JOIN to the latest
    evaluation (which may have changed since).
    """

    model_config = _TOLERANT

    signal: Signal
    signal_label: str | None = None
    fit_score: Score
    confidence: Score


# ---- Persisted (read) models ----------------------------------------------


class Job(BaseModel):
    """A persisted job row."""

    model_config = _TOLERANT

    id: int
    company: str
    role: str
    location: str | None = None
    work_type: str | None = None
    employment_type: str | None = None
    salary_range: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "USD"
    source: str | None = None
    source_url: str | None = None
    raw_content: str | None = None
    status: JobStatus = "decide"
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def _validate_salary_range(self) -> Job:
        _check_salary_monotonic(self.salary_min, self.salary_max)
        return self


class Evaluation(BaseModel):
    """A persisted evaluation row."""

    model_config = _TOLERANT

    id: int
    job_id: int
    kind: EvaluationKind
    fit_score: Score
    confidence: Score
    signal: Signal
    signal_label: str
    brief_recommendation: BriefRecommendation | None = None
    brief_reasons: BriefReasons = Field(default_factory=list)
    summary: str | None = None
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    evaluated_at: datetime


class TimelineEvent(BaseModel):
    """A persisted timeline-event row."""

    model_config = _TOLERANT

    id: int
    job_id: int
    label: str
    detail: str | None = None
    occurred_at: datetime
    source: str
    state: str = "done"


class Enrichment(BaseModel):
    """A persisted enrichment-result row."""

    model_config = _TOLERANT

    id: int
    job_id: int
    provider_key: str
    status: str = "done"
    result: dict[str, Any] | list[Any] | None = None
    source: str
    created_at: datetime
