"""Map ``(fit_score, confidence)`` to a signal + natural-tone label.

The label set is deliberately small and conversational, per the AI
discipline guardrails in the plan:

  Worth pursuing          ≥ 0.75 fit, sufficient confidence
  Worth a closer look     0.55 - 0.75 fit
  Mixed signals           0.40 - 0.55 fit
  Probably not            < 0.40 fit
  Need more info          confidence below the pending threshold,
                          regardless of fit score

A low-confidence result *always* surfaces as "Need more info" so the
user is never asked to act on a weak signal — confidence trumps fit.
This is the single tweak point referenced from the rest of the package;
verdict generation, composite merging, and any future calibration UI
reference these constants by name.
"""

from __future__ import annotations

from .models import Signal

# Bucket thresholds (closed-open intervals on fit_score).
# ``WORTH_PURSUING`` boundary is inclusive — fit==0.75 reads as "yes".
WORTH_PURSUING_THRESHOLD = 0.75
STRETCH_THRESHOLD = 0.55
MIXED_THRESHOLD = 0.40

# Below this confidence, the signal is "Need more info" regardless of
# fit score. Heuristic-only evaluations cap confidence at 0.5 by design,
# so a heuristic with weak evidence routinely falls below this line —
# which is correct: "I'd hold off until we have more info" is the
# advisory truth.
PENDING_CONFIDENCE_THRESHOLD = 0.30

# Natural-tone labels paired with each signal. The UI reads from this
# dict, never from raw signal codes, so changing copy is one edit.
SIGNAL_LABELS: dict[Signal, str] = {
    "yes": "Worth pursuing",
    "stretch": "Worth a closer look",
    "maybe": "Mixed signals",
    "no": "Probably not",
    "pending": "Need more info",
}


def signal_label_for(fit_score: float, confidence: float) -> tuple[Signal, str]:
    """Return ``(signal, signal_label)`` for the given numeric inputs.

    Inputs are expected to be in ``[0, 1]`` (validated at the model
    boundary via :data:`wisp.models.Score`); the function does not
    re-clamp. Low confidence ALWAYS wins — the surface message reflects
    epistemic state first, fit second.

    Examples
    --------
    >>> signal_label_for(0.82, 0.85)
    ('yes', 'Worth pursuing')
    >>> signal_label_for(0.62, 0.40)
    ('stretch', 'Worth a closer look')
    >>> signal_label_for(0.55, 0.20)
    ('pending', 'Need more info')
    >>> signal_label_for(0.25, 0.80)
    ('no', 'Probably not')
    """
    if confidence < PENDING_CONFIDENCE_THRESHOLD:
        return "pending", SIGNAL_LABELS["pending"]

    signal: Signal
    if fit_score >= WORTH_PURSUING_THRESHOLD:
        signal = "yes"
    elif fit_score >= STRETCH_THRESHOLD:
        signal = "stretch"
    elif fit_score >= MIXED_THRESHOLD:
        signal = "maybe"
    else:
        signal = "no"
    return signal, SIGNAL_LABELS[signal]
