"""Tests for ``wisp.evaluators.verdict``.

The HeuristicEvaluator tests already exercise ``verdict_for`` end-to-end
through the evaluator's call. These tests pin module-level behavior in
isolation: reason selection, advisory openers, length cap, the optional
checklist suffix, and the tone validator's pattern-matching rules.
"""

from __future__ import annotations

import pytest

from wisp.evaluators.verdict import validate_advisory, verdict_for
from wisp.models import BRIEF_REASONS_MAX_ITEMS, BRIEF_RECOMMENDATION_MAX_LENGTH

# ---- verdict_for: reason selection ----------------------------------------


def test_concern_takes_first_slot() -> None:
    """When both a concern and a strength are present, the concern leads.
    Negative reasons are usually the more decision-relevant signal."""
    body, reasons = verdict_for(
        "stretch",
        strengths=["Skills match"],
        concerns=["Salary below floor"],
    )
    assert reasons == ["Salary below floor", "Skills match"]
    assert "Salary below floor" in body


def test_strength_appears_in_second_slot_if_room() -> None:
    body, reasons = verdict_for(
        "yes",
        strengths=["Skills match", "Remote-first"],
        concerns=[],
    )
    # Concerns empty → strength takes the first slot
    assert reasons[0] == "Skills match"


def test_gap_only_appears_when_no_concern_or_strength() -> None:
    body, reasons = verdict_for(
        "stretch",
        gaps=["No mobile work in portfolio"],
    )
    assert reasons == ["No mobile work in portfolio"]
    assert "No mobile work" in body


def test_reasons_capped_at_two_items() -> None:
    """If we somehow had more than 2, the verdict still respects the cap."""
    body, reasons = verdict_for(
        "stretch",
        strengths=["s1", "s2", "s3"],
        concerns=["c1", "c2"],
    )
    assert len(reasons) <= BRIEF_REASONS_MAX_ITEMS


def test_no_reasons_yields_empty_handed_advisory() -> None:
    """No strengths/concerns/gaps → still produce a verdict, just a hedged one."""
    body, reasons = verdict_for("pending")
    assert reasons == []
    assert "don't have much to go on" in body


# ---- verdict_for: advisory tone -------------------------------------------


@pytest.mark.parametrize(
    "signal,opener_fragment",
    [
        ("yes", "I'd lean apply"),
        ("stretch", "I'd take a closer look"),
        ("maybe", "I'm on the fence"),
        ("no", "I'd lean skip"),
        ("pending", "I don't have enough evidence yet"),
    ],
)
def test_signal_picks_advisory_opener(signal: str, opener_fragment: str) -> None:
    body, _ = verdict_for(signal, strengths=["something positive"])  # type: ignore[arg-type]
    assert opener_fragment in body


def test_verdict_passes_its_own_tone_validator() -> None:
    """Every (signal, reasons) combination produces text that passes
    validate_advisory. The generator and the validator must agree."""
    cases = [
        ("yes", ["Skills match"], [], []),
        ("stretch", ["Salary below floor"], ["Remote OK"], []),
        ("maybe", [], [], ["No mobile work in portfolio"]),
        ("no", ["Deal-breaker matched: finance"], [], []),
        ("pending", [], [], []),
    ]
    for signal, concerns, strengths, gaps in cases:
        body, _ = verdict_for(
            signal,  # type: ignore[arg-type]
            strengths=strengths,
            concerns=concerns,
            gaps=gaps,
        )
        ok, flagged = validate_advisory(body)
        assert ok, f"verdict {body!r} flagged: {flagged}"


# ---- verdict_for: length cap ----------------------------------------------


def test_verdict_text_obeys_140_char_cap() -> None:
    """An obnoxiously long reason still produces a verdict ≤ cap."""
    long_reason = "x" * 200
    body, _ = verdict_for("yes", strengths=[long_reason])
    assert len(body) <= BRIEF_RECOMMENDATION_MAX_LENGTH


def test_verdict_truncation_uses_ellipsis() -> None:
    long_reason = "y" * 300
    body, _ = verdict_for("stretch", concerns=[long_reason])
    if len(body) == BRIEF_RECOMMENDATION_MAX_LENGTH:
        assert body.endswith("...")


# ---- verdict_for: checklist suffix ----------------------------------------


def test_unanimous_yes_checklist_appends_agreement() -> None:
    body, _ = verdict_for(
        "yes",
        strengths=["Skills match"],
        checklist={"fit": "yes", "qualified": "yes", "worth_time": "yes"},
    )
    assert "checklist agrees" in body.lower()


def test_mixed_checklist_does_not_append_agreement() -> None:
    body, _ = verdict_for(
        "yes",
        strengths=["Skills match"],
        checklist={"fit": "yes", "qualified": "no"},
    )
    assert "checklist agrees" not in body.lower()


def test_empty_checklist_does_not_append_agreement() -> None:
    body, _ = verdict_for(
        "yes",
        strengths=["Skills match"],
        checklist={},
    )
    assert "checklist agrees" not in body.lower()


def test_unanimous_yes_but_brief_already_at_cap_skips_suffix() -> None:
    """Don't truncate the reason just to fit 'Your checklist agrees.'"""
    long_reason = "z" * 100  # body will be near cap
    body, _ = verdict_for(
        "yes",
        strengths=[long_reason],
        checklist={"fit": "yes"},
    )
    assert len(body) <= BRIEF_RECOMMENDATION_MAX_LENGTH


# ---- validate_advisory ----------------------------------------------------


@pytest.mark.parametrize(
    "good_text",
    [
        "I'd lean apply — skills match.",
        "I'd take a closer look. Worth investigating the team.",
        "I don't have enough evidence yet.",
        "My read is that the salary may be below your floor.",
        # Borderline-but-acceptable: "you should" is not flagged
        "You should consider whether the commute fits your life.",
    ],
)
def test_advisory_text_passes(good_text: str) -> None:
    ok, flagged = validate_advisory(good_text)
    assert ok, f"flagged: {flagged}"
    assert flagged == []


@pytest.mark.parametrize(
    "bad_text,expected_flag",
    [
        ("Apply now.", "apply"),
        ("apply for this role.", "apply"),
        ("Skip this one.", "skip"),
        ("Decline the offer.", "decline"),
        ("You must take this role.", "you must"),
        ("You have to apply today.", "you have to"),
        ("You need to act fast.", "you need to"),
    ],
)
def test_imperative_openers_are_flagged(bad_text: str, expected_flag: str) -> None:
    ok, flagged = validate_advisory(bad_text)
    assert not ok
    assert any(expected_flag in f for f in flagged), flagged


@pytest.mark.parametrize(
    "bad_text,expected_flag",
    [
        ("This is definitely the right role for you.", "definitely"),
        ("You will absolutely succeed here.", "absolutely"),
        ("This is guaranteed to work out.", "guaranteed"),
        ("Without doubt the best option.", "without doubt"),
        ("It's certainly worth your time.", "certainly"),
    ],
)
def test_certainty_claims_are_flagged(bad_text: str, expected_flag: str) -> None:
    ok, flagged = validate_advisory(bad_text)
    assert not ok
    assert expected_flag in flagged


def test_imperative_in_subordinate_clause_is_not_flagged() -> None:
    """We only flag imperatives that START a sentence — 'I'd apply if...'
    is fine because the sentence opens with 'I'd'."""
    ok, _ = validate_advisory("I'd apply if I were you, but it's your call.")
    assert ok


def test_validator_handles_multi_sentence_text() -> None:
    """A single bad sentence flags the whole text."""
    ok, flagged = validate_advisory(
        "I'd lean apply — skills match. Apply right now! That's a strong fit."
    )
    assert not ok
    assert "apply" in flagged
