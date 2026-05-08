"""Tests for ``wisp.signals.signal_label_for``.

Pin every bucket boundary and the low-confidence override so a future
threshold tweak is intentional, not an accident.
"""

from __future__ import annotations

import pytest

from wisp.signals import (
    MIXED_THRESHOLD,
    PENDING_CONFIDENCE_THRESHOLD,
    SIGNAL_LABELS,
    STRETCH_THRESHOLD,
    WORTH_PURSUING_THRESHOLD,
    signal_label_for,
)

# Confidence well above the pending threshold so the fit-score bucket
# is the active branch in the function.
HIGH_CONF = 0.90


@pytest.mark.parametrize(
    ("fit_score", "expected_signal", "expected_label"),
    [
        # Top bucket: ≥ 0.75 → "yes" / "Worth pursuing"
        (1.00, "yes", "Worth pursuing"),
        (0.90, "yes", "Worth pursuing"),
        (WORTH_PURSUING_THRESHOLD, "yes", "Worth pursuing"),  # boundary inclusive
        # Stretch: 0.55 ≤ fit < 0.75 → "Worth a closer look"
        (0.7499, "stretch", "Worth a closer look"),
        (0.65, "stretch", "Worth a closer look"),
        (STRETCH_THRESHOLD, "stretch", "Worth a closer look"),  # boundary inclusive
        # Mixed: 0.40 ≤ fit < 0.55
        (0.5499, "maybe", "Mixed signals"),
        (0.45, "maybe", "Mixed signals"),
        (MIXED_THRESHOLD, "maybe", "Mixed signals"),  # boundary inclusive
        # Bottom bucket: < 0.40 → "Probably not"
        (0.3999, "no", "Probably not"),
        (0.20, "no", "Probably not"),
        (0.00, "no", "Probably not"),
    ],
)
def test_fit_score_buckets(
    fit_score: float, expected_signal: str, expected_label: str
) -> None:
    """Every documented bucket boundary returns the right (signal, label)."""
    signal, label = signal_label_for(fit_score, HIGH_CONF)
    assert signal == expected_signal
    assert label == expected_label


# ---- Low-confidence override ----------------------------------------------


def test_low_confidence_overrides_high_fit_score() -> None:
    """A great fit score with weak evidence is still 'pending' — the
    advisory truth is 'I'd hold off until we have more info'."""
    signal, label = signal_label_for(fit_score=0.95, confidence=0.10)
    assert signal == "pending"
    assert label == "Need more info"


def test_low_confidence_overrides_at_each_bucket() -> None:
    """Verify the override fires across the fit-score range, not just at
    the top."""
    weak = PENDING_CONFIDENCE_THRESHOLD - 0.01
    for fit in (0.95, 0.65, 0.50, 0.20):
        signal, label = signal_label_for(fit, weak)
        assert signal == "pending", f"fit={fit} should override to pending"
        assert label == "Need more info"


def test_pending_confidence_threshold_boundary_is_exclusive() -> None:
    """At exactly the threshold, confidence is "enough" — the fit bucket
    decides. One epsilon below, the override fires."""
    signal_at_boundary, _ = signal_label_for(0.20, PENDING_CONFIDENCE_THRESHOLD)
    assert signal_at_boundary == "no"  # bucket wins; 0.20 fit < MIXED_THRESHOLD

    signal_below, _ = signal_label_for(0.20, PENDING_CONFIDENCE_THRESHOLD - 0.0001)
    assert signal_below == "pending"  # override wins


# ---- Label table integrity ------------------------------------------------


def test_signal_labels_dict_covers_every_signal_value() -> None:
    """SIGNAL_LABELS is the source of truth for UI copy. Every Signal
    literal must have an entry — otherwise the UI would render an empty
    label for that case."""
    expected_signals = {"yes", "stretch", "maybe", "no", "pending"}
    assert set(SIGNAL_LABELS.keys()) == expected_signals


def test_signal_labels_are_advisory_in_tone() -> None:
    """No imperative verbs ('Apply', 'Skip', 'Decline') — the UX value
    is that AI advises, never commands. This test guards against a
    well-meaning copy edit that breaks the convention."""
    forbidden = {"apply", "skip", "decline", "accept", "reject"}
    for label in SIGNAL_LABELS.values():
        words = {w.strip(".,!").lower() for w in label.split()}
        assert not (words & forbidden), f"label {label!r} uses imperative copy"
