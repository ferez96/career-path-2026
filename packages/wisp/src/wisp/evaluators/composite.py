"""Composite-evaluation orchestrator.

Runs the always-on :class:`HeuristicEvaluator`, optionally runs an AI
evaluator (M4), and merges them into a third "composite"
:class:`EvaluationInput`. All three rows persist via
:meth:`SqliteVaultAdapter.add_evaluation` so disagreement remains
auditable in the cold-storage timeline.

In M3 only the heuristic-only path runs (no AI evaluator implemented
yet). The merge logic for agreement / disagreement is designed and
unit-tested via direct calls to :func:`merge` so M4 is a drop-in.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import Profile
from ..models import EvaluationInput, Job
from ..signals import SIGNAL_LABELS, signal_label_for
from .base import Evaluator
from .verdict import verdict_for

# Composite confidence ceiling. Agreement between heuristic + AI
# raises us up to here; we never claim 1.0 because two evaluators
# agreeing is still two evaluators agreeing, not the ground truth.
COMPOSITE_CONFIDENCE_CAP = 0.95

# Bonus added when heuristic + AI agree on signal AND their fit_scores
# are within AGREEMENT_FIT_TOLERANCE of each other.
AGREEMENT_BONUS = 0.05
AGREEMENT_FIT_TOLERANCE = 0.15


@dataclass
class CompositeResult:
    """Bundle returned by :func:`evaluate`. The route layer persists each
    populated row via :meth:`VaultAdapter.add_evaluation`."""

    heuristic: EvaluationInput
    ai: EvaluationInput | None
    composite: EvaluationInput


def evaluate(
    job: Job,
    profile: Profile,
    heuristic: Evaluator,
    ai: Evaluator | None = None,
    checklist: dict[str, str] | None = None,
) -> CompositeResult:
    """Run heuristic (+ optional AI), merge into a composite.

    The heuristic is always invoked. The AI is invoked only if it's
    provided AND :meth:`Evaluator.is_available` returns True; this
    matches the calm-UX rule "Wisp works without AI".
    """
    heuristic_eval = heuristic.evaluate(job, profile, checklist)

    ai_eval: EvaluationInput | None = None
    if ai is not None and ai.is_available():
        ai_eval = ai.evaluate(job, profile, checklist)

    composite_eval = merge(heuristic_eval, ai_eval, checklist)
    return CompositeResult(
        heuristic=heuristic_eval,
        ai=ai_eval,
        composite=composite_eval,
    )


def merge(
    heuristic: EvaluationInput,
    ai: EvaluationInput | None,
    checklist: dict[str, str] | None = None,
) -> EvaluationInput:
    """Merge a heuristic + optional AI eval into a composite eval row.

    Three branches:

    1. **AI absent.** Composite mirrors the heuristic with ``kind`` flipped
       to "composite". Reasons / strengths / gaps / concerns flow through.

    2. **AI present, agrees with heuristic** (same ``signal`` AND
       ``|fit_h - fit_ai| ≤ AGREEMENT_FIT_TOLERANCE``). fit_score is the
       average; confidence is the max of the two plus ``AGREEMENT_BONUS``,
       capped at ``COMPOSITE_CONFIDENCE_CAP``. Signal stays as the agreed
       value.

    3. **AI present, disagrees.** fit_score is the average; confidence
       drops to the min of the two; signal is forced to "pending". The
       UI surfaces both views in cold storage; the user is asked to weigh
       in via the checklist.
    """
    if ai is None:
        return _passthrough_to_composite(heuristic, checklist)

    agree = (
        heuristic.signal == ai.signal
        and abs(heuristic.fit_score - ai.fit_score) <= AGREEMENT_FIT_TOLERANCE
    )

    fit_score = (heuristic.fit_score + ai.fit_score) / 2

    if agree:
        confidence = min(
            COMPOSITE_CONFIDENCE_CAP,
            max(heuristic.confidence, ai.confidence) + AGREEMENT_BONUS,
        )
        signal = heuristic.signal
        signal_label = SIGNAL_LABELS.get(signal, heuristic.signal_label)
    else:
        confidence = min(heuristic.confidence, ai.confidence)
        signal = "pending"
        signal_label = SIGNAL_LABELS["pending"]

    # Re-bucket the merged (fit_score, confidence) — this lets the
    # low-confidence override fire even on agreement, e.g. when both
    # evaluators say "yes" but with weak evidence.
    rebucketed_signal, rebucketed_label = signal_label_for(fit_score, confidence)
    if rebucketed_signal == "pending":
        signal = "pending"
        signal_label = rebucketed_label

    strengths = _dedup_concat(heuristic.strengths, ai.strengths)
    gaps = _dedup_concat(heuristic.gaps, ai.gaps)
    concerns = _dedup_concat(heuristic.concerns, ai.concerns)
    cautions = _dedup_concat(heuristic.cautions, ai.cautions)
    evidence = list(heuristic.evidence) + list(ai.evidence)

    if not agree:
        # Surface the disagreement explicitly in the cold-storage concerns
        # list so the user can see WHY this rolled to pending.
        concerns.insert(
            0,
            f"Heuristic says {heuristic.signal!r}, AI says {ai.signal!r} — "
            f"treating as pending until resolved",
        )

    brief, reasons = verdict_for(
        signal,
        strengths=strengths,
        concerns=concerns,
        gaps=gaps,
        checklist=checklist,
    )

    return EvaluationInput(
        kind="composite",
        fit_score=fit_score,
        confidence=confidence,
        signal=signal,
        signal_label=signal_label,
        brief_recommendation=brief,
        brief_reasons=reasons,
        summary=ai.summary or heuristic.summary,
        strengths=strengths,
        gaps=gaps,
        concerns=concerns,
        cautions=cautions,
        recommendation=ai.recommendation or heuristic.recommendation,
        evidence=evidence,
    )


def _passthrough_to_composite(
    heuristic: EvaluationInput,
    checklist: dict[str, str] | None,
) -> EvaluationInput:
    """Heuristic-only composite. We don't blindly copy the heuristic's
    verdict because the composite carries the (optional) checklist suffix
    that the heuristic doesn't see."""
    brief, reasons = verdict_for(
        heuristic.signal,
        strengths=heuristic.strengths,
        concerns=heuristic.concerns,
        gaps=heuristic.gaps,
        checklist=checklist,
    )
    return EvaluationInput(
        kind="composite",
        fit_score=heuristic.fit_score,
        confidence=heuristic.confidence,
        signal=heuristic.signal,
        signal_label=heuristic.signal_label,
        brief_recommendation=brief,
        brief_reasons=reasons,
        summary=heuristic.summary,
        strengths=list(heuristic.strengths),
        gaps=list(heuristic.gaps),
        concerns=list(heuristic.concerns),
        cautions=list(heuristic.cautions),
        recommendation=heuristic.recommendation,
        evidence=list(heuristic.evidence),
    )


def _dedup_concat(a: list[str], b: list[str]) -> list[str]:
    """Concatenate two lists preserving order, dropping duplicates."""
    seen: set[str] = set()
    out: list[str] = []
    for item in (*a, *b):
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out
