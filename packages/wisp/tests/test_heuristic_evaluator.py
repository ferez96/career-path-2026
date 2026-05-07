"""Tests for :class:`wisp.evaluators.HeuristicEvaluator`.

Each rule (deal-breaker, salary, location, keyword overlap) and the
combined soft-scoring path is exercised on a fresh evaluator instance.
The HeuristicEvaluator is pure-Python and deterministic — no fixtures
needed beyond a couple of constructor helpers.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from wisp.config import Profile
from wisp.evaluators import Evaluator, HeuristicEvaluator
from wisp.evaluators.heuristics import (
    HARD_RULE_CONFIDENCE,
    HEURISTIC_CONFIDENCE_CAP,
    SPARSE_PROFILE_CONFIDENCE,
)
from wisp.models import Job


def _job(
    *,
    company: str = "Linear",
    role: str = "Senior Product Designer",
    location: str | None = "Remote",
    work_type: str | None = "remote",
    salary_min: int | None = None,
    salary_max: int | None = None,
    salary_currency: str = "USD",
    raw_content: str | None = None,
) -> Job:
    now = datetime.now(timezone.utc)
    return Job(
        id=1,
        company=company,
        role=role,
        location=location,
        work_type=work_type,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        raw_content=raw_content,
        created_at=now,
        updated_at=now,
    )


def _profile(
    *,
    target_role: str = "Senior Product Designer",
    top_skills: list[str] | None = None,
    deal_breakers: list[str] | None = None,
    salary_floor: int | None = None,
    salary_floor_currency: str = "USD",
    location_preference: str = "",
) -> Profile:
    # Profile validators normalize tags (lowercase + strip + dedupe);
    # we feed raw strings and let the model do the work.
    return Profile(
        target_role=target_role,
        top_skills=top_skills or [],
        deal_breakers=deal_breakers or [],
        salary_floor=salary_floor,
        salary_floor_currency=salary_floor_currency,
        location_preference=location_preference,
    )


# ---- Protocol conformance --------------------------------------------------


def test_heuristic_evaluator_satisfies_protocol() -> None:
    """Runtime structural check — catches a missing method here, not at
    composite-merge time."""
    assert isinstance(HeuristicEvaluator(), Evaluator)


def test_heuristic_evaluator_is_always_available() -> None:
    assert HeuristicEvaluator().is_available() is True


def test_heuristic_evaluator_kind_is_heuristic() -> None:
    assert HeuristicEvaluator().kind == "heuristic"


# ---- Deal-breaker hard rule -----------------------------------------------


def test_deal_breaker_match_short_circuits_to_no() -> None:
    """A deal-breaker hit produces signal='no' with hard-rule confidence,
    regardless of how well the rest of the profile matches."""
    job = _job(
        company="Goldman Sachs",
        raw_content="Building distributed trading systems for the finance industry.",
    )
    profile = _profile(
        deal_breakers=["finance", "gambling"],
        top_skills=["distributed systems"],  # would otherwise score high
    )
    eval_ = HeuristicEvaluator().evaluate(job, profile)

    assert eval_.signal == "no"
    assert eval_.signal_label == "Probably not"
    assert eval_.fit_score == 0.0
    assert eval_.confidence == HARD_RULE_CONFIDENCE
    # Deal-breaker is named in both the verdict and the reasons
    assert "finance" in (eval_.brief_recommendation or "")
    assert any("finance" in c.lower() for c in eval_.concerns)


def test_deal_breaker_unmatched_does_not_fire() -> None:
    """If the JD doesn't mention any deal-breaker tag, the soft path runs."""
    job = _job(raw_content="Linear is a tool for high-performance teams.")
    profile = _profile(
        deal_breakers=["finance"],
        top_skills=["design systems"],
    )
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert eval_.signal != "no" or eval_.confidence < HARD_RULE_CONFIDENCE


# ---- Salary check ----------------------------------------------------------


def test_salary_max_below_floor_caps_fit_score() -> None:
    """Strong negative when the JD ceiling is below profile floor (same
    currency). fit_score is clamped to ≤0.30 via the soft penalty."""
    job = _job(
        salary_min=70_000,
        salary_max=85_000,
        raw_content="Senior product designer role.",
    )
    profile = _profile(
        salary_floor=120_000,
        top_skills=["design systems"],
        target_role="Senior Product Designer",
    )
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert eval_.fit_score <= 0.30
    assert any("salary" in c.lower() for c in eval_.concerns)


def test_salary_above_floor_is_a_strength() -> None:
    job = _job(salary_min=140_000, salary_max=180_000)
    profile = _profile(salary_floor=120_000)
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert any("salary" in s.lower() for s in eval_.strengths)


def test_salary_check_skipped_on_currency_mismatch() -> None:
    """We don't carry a currency-conversion table in v1 — different
    currencies must NOT produce a salary signal either way."""
    job = _job(salary_min=20_000_000, salary_max=30_000_000, salary_currency="VND")
    profile = _profile(salary_floor=120_000, salary_floor_currency="USD")
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert all("salary" not in s.lower() for s in eval_.strengths)
    assert all("salary" not in c.lower() for c in eval_.concerns)


def test_salary_check_skipped_when_profile_floor_unset() -> None:
    job = _job(salary_min=70_000, salary_max=85_000)
    profile = _profile(salary_floor=None)
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert all("salary" not in c.lower() for c in eval_.concerns)


# ---- Location check --------------------------------------------------------


def test_remote_only_vs_onsite_is_a_concern() -> None:
    job = _job(work_type="onsite", location="New York, NY")
    profile = _profile(location_preference="remote-only")
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert any("remote" in c.lower() for c in eval_.concerns)
    assert eval_.fit_score <= 0.30


def test_remote_only_matched_is_a_strength() -> None:
    job = _job(work_type="remote", location="Remote")
    profile = _profile(location_preference="remote-only")
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert any("remote" in s.lower() for s in eval_.strengths)


# ---- Keyword overlap (soft path) ------------------------------------------


def test_strong_match_produces_high_fit_score() -> None:
    """Profile target role appears in JD AND every top skill is mentioned —
    the soft scoring path should land in stretch+ territory."""
    job = _job(
        role="Senior Product Designer",
        raw_content=(
            "Senior Product Designer at Linear. You'll work on design "
            "systems and cross-functional prototyping with engineers."
        ),
    )
    profile = _profile(
        target_role="Senior Product Designer",
        top_skills=["design systems", "prototyping"],
    )
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    # 1.0 skill score * 0.6 + 1.0 role score * 0.4 = 1.0
    assert eval_.fit_score == pytest.approx(1.0, abs=0.01)
    assert eval_.confidence == HEURISTIC_CONFIDENCE_CAP


def test_partial_skill_match_produces_proportional_fit_score() -> None:
    """1 of 2 skills matches → 0.5 skill score → 0.6*0.5 + 0.4*1.0 = 0.7"""
    job = _job(
        raw_content=(
            "Senior Product Designer role. Requires strong "
            "design systems experience."
        ),
    )
    profile = _profile(
        target_role="Senior Product Designer",
        top_skills=["design systems", "prototyping"],
    )
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert eval_.fit_score == pytest.approx(0.7, abs=0.01)
    # The unmatched skill shows up in gaps
    assert any("prototyping" in g for g in eval_.gaps)


def test_sparse_profile_yields_low_confidence() -> None:
    """No top_skills, no target_role → confidence floor; signal goes
    pending via the low-confidence override in signal_label_for."""
    job = _job(raw_content="Some JD text.")
    profile = _profile(target_role="", top_skills=[])
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert eval_.confidence == SPARSE_PROFILE_CONFIDENCE
    # SPARSE_PROFILE_CONFIDENCE (0.20) < PENDING_CONFIDENCE_THRESHOLD (0.30)
    # so signal_label_for routes to "pending" / "Need more info"
    assert eval_.signal == "pending"
    assert eval_.signal_label == "Need more info"


# ---- Output shape ----------------------------------------------------------


def test_evaluation_input_obeys_brief_caps() -> None:
    """The verdict text must fit the hot-brief 140-char cap; reasons ≤2."""
    profile = _profile(
        target_role="Senior Product Designer",
        top_skills=["design systems"],
    )
    job = _job(raw_content="Senior Product Designer role using design systems daily.")
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert eval_.brief_recommendation is not None
    assert len(eval_.brief_recommendation) <= 140
    assert len(eval_.brief_reasons) <= 2


def test_brief_recommendation_uses_advisory_tone() -> None:
    """Verdict text must NOT start with imperative verbs."""
    profile = _profile(top_skills=["design systems"], target_role="x")
    job = _job(raw_content="design systems x")
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    text = (eval_.brief_recommendation or "").lower()
    forbidden_openers = ("apply", "skip ", "decline", "you must", "you should")
    assert not any(text.startswith(f) for f in forbidden_openers), text


def test_kind_is_heuristic() -> None:
    profile = _profile()
    job = _job()
    eval_ = HeuristicEvaluator().evaluate(job, profile)
    assert eval_.kind == "heuristic"
