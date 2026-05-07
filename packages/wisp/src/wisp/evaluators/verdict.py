"""Advisory-tone verdict text + post-parse tone validator.

The verdict generator turns a (signal, strengths, concerns, gaps,
optional checklist) tuple into a hot-brief verdict line and a 1-2
item reasons list. Heuristic and AI evaluators both produce their
strengths/concerns/gaps separately and call into here for the
human-facing copy.

The tone validator scans verdict text for imperative or certainty
phrasing and reports flagged terms. AI evaluators in M4 use it as
a post-parse guard: if an LLM returns "Apply now!" we strip the
verdict, downgrade confidence, and let the user see a softer fallback.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from ..models import (
    BRIEF_REASONS_MAX_ITEMS,
    BRIEF_RECOMMENDATION_MAX_LENGTH,
    Signal,
)

# Maps each signal to an advisory opener. NEVER imperative.
_OPENERS: dict[Signal, str] = {
    "yes": "I'd lean apply",
    "stretch": "I'd take a closer look",
    "maybe": "I'm on the fence",
    "no": "I'd lean skip",
    "pending": "I don't have enough evidence yet",
}

_FALLBACK_OPENER = "My read is"

# Forbidden patterns (lowercase) — case-insensitive substring or prefix
# matches. Imperative openers are flagged when they START a sentence
# (after stripping). Certainty claims are flagged anywhere in the text.
_IMPERATIVE_OPENERS = (
    "apply",
    "skip ",
    "skip.",
    "decline",
    "accept",
    "reject",
    "you must",
    "you have to",
    "you need to",
)
_CERTAINTY_CLAIMS = (
    "definitely",
    "certainly",
    "absolutely",
    "for sure",
    "guaranteed",
    "without doubt",
)


def verdict_for(
    signal: Signal,
    strengths: Iterable[str] = (),
    concerns: Iterable[str] = (),
    gaps: Iterable[str] = (),
    checklist: dict[str, str] | None = None,
) -> tuple[str, list[str]]:
    """Build an advisory-tone (brief_recommendation, brief_reasons) pair.

    Reason selection: surface at most one concern (if any) and then one
    strength (if any). If the result is empty, fall back to the first
    gap so the user sees *something* in the hot brief.

    Verdict text is capped at :data:`BRIEF_RECOMMENDATION_MAX_LENGTH`
    via tail-truncation with an ellipsis.

    The optional ``checklist`` is consulted only for verdict text — when
    every checklist answer is "yes", the verdict acknowledges that
    agreement explicitly. It does not change the signal (the caller
    owns that).
    """
    concerns_list = list(concerns)
    strengths_list = list(strengths)
    gaps_list = list(gaps)

    reasons: list[str] = []
    if concerns_list:
        reasons.append(concerns_list[0])
    if strengths_list and len(reasons) < BRIEF_REASONS_MAX_ITEMS:
        reasons.append(strengths_list[0])
    if not reasons and gaps_list:
        reasons.append(gaps_list[0])
    reasons = reasons[:BRIEF_REASONS_MAX_ITEMS]

    opener = _OPENERS.get(signal, _FALLBACK_OPENER)
    if reasons:
        body = f"{opener} — {reasons[0]}."
    else:
        body = f"{opener}, though I don't have much to go on yet."

    if checklist and _checklist_unanimously_positive(checklist):
        suffix = " Your checklist agrees."
        if len(body) + len(suffix) <= BRIEF_RECOMMENDATION_MAX_LENGTH:
            body += suffix

    if len(body) > BRIEF_RECOMMENDATION_MAX_LENGTH:
        body = body[: BRIEF_RECOMMENDATION_MAX_LENGTH - 3] + "..."
    return body, reasons


def _checklist_unanimously_positive(checklist: dict[str, str]) -> bool:
    """Tiny heuristic: every populated answer is 'yes' (case-insensitive).

    Empty checklist returns False (no signal of agreement)."""
    answers = [v for v in checklist.values() if v]
    return bool(answers) and all(v.strip().lower() == "yes" for v in answers)


def validate_advisory(text: str) -> tuple[bool, list[str]]:
    """Return ``(ok, flagged_terms)``.

    ``ok`` is True when the text contains no obvious imperative openers
    or certainty claims. ``flagged_terms`` lists every match — useful
    for logging when an AI evaluator is misbehaving.

    The check is conservative: we only flag patterns that are very
    likely imperative ("Apply.", "You must …") or certainty-laden
    ("definitely", "guaranteed"). Borderline phrasings ("you should",
    "I'd say it works") pass — pattern-based tone checking can't
    capture nuance, and false positives are worse than false negatives.
    """
    flagged: list[str] = []

    # Sentence-initial imperatives. Split on common sentence boundaries.
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    for sentence in sentences:
        head = sentence.strip().lower()
        for op in _IMPERATIVE_OPENERS:
            if head.startswith(op):
                flagged.append(op.strip())
                break

    # Certainty claims anywhere in the text.
    text_lower = text.lower()
    for claim in _CERTAINTY_CLAIMS:
        if claim in text_lower:
            flagged.append(claim)

    return (not flagged), flagged
