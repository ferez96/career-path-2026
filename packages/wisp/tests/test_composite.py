"""Tests for ``wisp.evaluators.composite``.

Two layers:
  1. ``evaluate`` end-to-end with a heuristic and (optionally) a fake
     AI evaluator — proves the orchestration.
  2. ``merge`` direct-call tests for agreement / disagreement /
     confidence-bonus / re-bucket-on-low-confidence — proves the merge
     math without spinning up the heuristic.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from wisp.config import Profile
from wisp.evaluators import (
    CompositeResult,
    Evaluator,
    HeuristicEvaluator,
    evaluate,
    merge,
)
from wisp.evaluators.composite import (
    AGREEMENT_BONUS,
    AGREEMENT_FIT_TOLERANCE,
    COMPOSITE_CONFIDENCE_CAP,
)
from wisp.models import EvaluationInput, Job

# ---- Helpers --------------------------------------------------------------


def _job() -> Job:
    now = datetime.now(timezone.utc)
    return Job(
        id=1,
        company="Linear",
        role="Senior Product Designer",
        location="Remote",
        work_type="remote",
        raw_content="Senior Product Designer role using design systems daily.",
        created_at=now,
        updated_at=now,
    )


def _profile(**kwargs: object) -> Profile:
    defaults: dict[str, object] = {
        "target_role": "Senior Product Designer",
        "top_skills": ["design systems"],
    }
    defaults.update(kwargs)
    return Profile(**defaults)  # type: ignore[arg-type]


def _fake_eval(
    *,
    kind: str = "ai",
    fit_score: float = 0.8,
    confidence: float = 0.7,
    signal: str = "yes",
    signal_label: str = "Worth pursuing",
    strengths: list[str] | None = None,
    concerns: list[str] | None = None,
    gaps: list[str] | None = None,
    summary: str | None = "AI summary text",
) -> EvaluationInput:
    return EvaluationInput(
        kind=kind,  # type: ignore[arg-type]
        fit_score=fit_score,
        confidence=confidence,
        signal=signal,  # type: ignore[arg-type]
        signal_label=signal_label,
        strengths=strengths or [],
        concerns=concerns or [],
        gaps=gaps or [],
        summary=summary,
    )


class _FakeAIEvaluator:
    """Stand-in for a real AI evaluator. Always available, returns the
    EvaluationInput it was constructed with."""

    name: str = "fake-ai"

    def __init__(self, eval_: EvaluationInput, available: bool = True) -> None:
        self._eval = eval_
        self._available = available

    @property
    def kind(self) -> str:
        return "ai"

    def is_available(self) -> bool:
        return self._available

    def evaluate(
        self,
        job: Job,
        profile: Profile,
        checklist: dict[str, str] | None = None,
    ) -> EvaluationInput:
        del job, profile, checklist  # fake just returns canned output
        return self._eval


# ---- evaluate (orchestration) ---------------------------------------------


def test_evaluate_runs_heuristic_only_by_default() -> None:
    result = evaluate(_job(), _profile(), heuristic=HeuristicEvaluator())
    assert isinstance(result, CompositeResult)
    assert result.heuristic.kind == "heuristic"
    assert result.ai is None
    assert result.composite.kind == "composite"


def test_evaluate_skips_ai_when_unavailable() -> None:
    """An AI evaluator that reports is_available()=False must NOT be
    invoked. Confirms the calm-UX rule "Wisp works without AI"."""
    fake_eval = _fake_eval(strengths=["AI strength"])
    fake_ai = _FakeAIEvaluator(fake_eval, available=False)

    result = evaluate(
        _job(),
        _profile(),
        heuristic=HeuristicEvaluator(),
        ai=fake_ai,
    )
    assert result.ai is None
    # Composite mirrors heuristic — no "AI strength" leaked
    assert "AI strength" not in result.composite.strengths


def test_evaluate_invokes_ai_when_available() -> None:
    fake_eval = _fake_eval(strengths=["AI strength"])
    fake_ai = _FakeAIEvaluator(fake_eval, available=True)

    result = evaluate(
        _job(),
        _profile(),
        heuristic=HeuristicEvaluator(),
        ai=fake_ai,
    )
    assert result.ai is not None
    assert "AI strength" in result.composite.strengths


# ---- merge: heuristic-only path ------------------------------------------


def test_merge_heuristic_only_passes_through_to_composite() -> None:
    h = _fake_eval(
        kind="heuristic", fit_score=0.7, confidence=0.5,
        signal="stretch", signal_label="Worth a closer look",
        strengths=["Skills match"],
    )
    c = merge(h, ai=None)
    assert c.kind == "composite"
    assert c.fit_score == 0.7
    assert c.confidence == 0.5
    assert c.signal == "stretch"
    assert c.strengths == ["Skills match"]


def test_merge_heuristic_only_applies_checklist_suffix() -> None:
    """Heuristic alone passes through, but the composite verdict ALSO
    incorporates the checklist (which the heuristic itself ignores)."""
    h = _fake_eval(
        kind="heuristic", fit_score=0.8, confidence=0.5,
        signal="yes", strengths=["Skills match"],
    )
    c = merge(
        h, ai=None,
        checklist={"fit": "yes", "qualified": "yes", "worth_time": "yes"},
    )
    assert "checklist agrees" in (c.brief_recommendation or "").lower()


# ---- merge: agreement boost ----------------------------------------------


def test_merge_agreement_boosts_confidence() -> None:
    """Same signal AND fit scores within tolerance → confidence
    bumps by AGREEMENT_BONUS, capped at COMPOSITE_CONFIDENCE_CAP."""
    h = _fake_eval(kind="heuristic", fit_score=0.80, confidence=0.50, signal="yes")
    a = _fake_eval(kind="ai",        fit_score=0.78, confidence=0.70, signal="yes")
    c = merge(h, ai=a)
    expected = min(COMPOSITE_CONFIDENCE_CAP, 0.70 + AGREEMENT_BONUS)
    assert c.confidence == pytest.approx(expected)
    assert c.signal == "yes"
    # fit_score = mean
    assert c.fit_score == pytest.approx(0.79)


def test_merge_agreement_caps_at_composite_ceiling() -> None:
    """Agreement bonus must NEVER push confidence past the ceiling."""
    h = _fake_eval(confidence=0.94, signal="yes", fit_score=0.85)
    a = _fake_eval(confidence=0.94, signal="yes", fit_score=0.85)
    c = merge(h, ai=a)
    assert c.confidence == COMPOSITE_CONFIDENCE_CAP


# ---- merge: disagreement → pending ---------------------------------------


def test_merge_disagreement_forces_pending_signal() -> None:
    h = _fake_eval(signal="yes", fit_score=0.80, confidence=0.50)
    a = _fake_eval(signal="no",  fit_score=0.30, confidence=0.70)
    c = merge(h, ai=a)
    assert c.signal == "pending"
    assert c.signal_label == "Need more info"


def test_merge_disagreement_drops_confidence_to_min() -> None:
    h = _fake_eval(signal="yes", fit_score=0.80, confidence=0.50)
    a = _fake_eval(signal="no",  fit_score=0.30, confidence=0.85)
    c = merge(h, ai=a)
    assert c.confidence == 0.50  # min of the two


def test_merge_disagreement_surfaces_both_views_in_concerns() -> None:
    h = _fake_eval(signal="yes", fit_score=0.80, confidence=0.50)
    a = _fake_eval(signal="no",  fit_score=0.30, confidence=0.70)
    c = merge(h, ai=a)
    assert any(
        "heuristic says" in concern.lower() and "ai says" in concern.lower()
        for concern in c.concerns
    )


def test_merge_signals_within_fit_tolerance_still_agree() -> None:
    """Same signal but fit scores beyond AGREEMENT_FIT_TOLERANCE are
    treated as disagreement (signal stays the same but the math is wonky)."""
    h = _fake_eval(signal="yes", fit_score=0.95, confidence=0.50)
    a = _fake_eval(
        signal="yes",
        fit_score=0.95 - AGREEMENT_FIT_TOLERANCE - 0.01,  # just outside tolerance
        confidence=0.70,
    )
    c = merge(h, ai=a)
    # fit is too far apart → treated as disagreement → pending
    assert c.signal == "pending"


# ---- merge: low-confidence override after merge -------------------------


def test_merge_routes_to_pending_when_combined_confidence_is_below_threshold() -> None:
    """Even if both agree on signal='yes', a tiny combined confidence
    must trigger the low-confidence override (signal_label_for)."""
    h = _fake_eval(signal="yes", fit_score=0.80, confidence=0.10)
    a = _fake_eval(signal="yes", fit_score=0.80, confidence=0.10)
    c = merge(h, ai=a)
    # Combined confidence = max(0.10, 0.10) + 0.05 = 0.15 < 0.30 threshold
    # → low-confidence override fires; signal flips to pending
    assert c.signal == "pending"
    assert c.signal_label == "Need more info"


# ---- merge: structured field handling ----------------------------------


def test_merge_dedups_strengths_across_evaluators() -> None:
    h = _fake_eval(strengths=["Skills match", "Remote OK"], signal="yes", confidence=0.5, fit_score=0.8)
    a = _fake_eval(strengths=["Skills match", "Strong team"], signal="yes", confidence=0.7, fit_score=0.8)
    c = merge(h, ai=a)
    assert c.strengths == ["Skills match", "Remote OK", "Strong team"]


def test_merge_prefers_ai_summary_over_heuristic() -> None:
    h = _fake_eval(summary="heuristic summary", signal="yes", fit_score=0.8, confidence=0.5)
    a = _fake_eval(summary="AI summary", signal="yes", fit_score=0.8, confidence=0.7)
    c = merge(h, ai=a)
    assert c.summary == "AI summary"


def test_merge_falls_back_to_heuristic_summary_when_ai_summary_is_none() -> None:
    h = _fake_eval(summary="heuristic summary", signal="yes", fit_score=0.8, confidence=0.5)
    a = _fake_eval(summary=None, signal="yes", fit_score=0.8, confidence=0.7)
    c = merge(h, ai=a)
    assert c.summary == "heuristic summary"


# ---- Evaluator Protocol still satisfied by the fake ---------------------


def test_fake_ai_evaluator_satisfies_protocol() -> None:
    """The fake we use in these tests must look like a real Evaluator
    so the orchestration's isinstance check (if any) doesn't reject it."""
    fake = _FakeAIEvaluator(_fake_eval())
    assert isinstance(fake, Evaluator)
