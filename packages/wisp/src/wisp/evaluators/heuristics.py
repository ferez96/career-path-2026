"""HeuristicEvaluator — always-on, no AI required.

Combines four kinds of checks against the job + profile:

  1. **Deal-breaker hits.** Substring match against ``profile.deal_breakers``
     in the job text. A hit is a hard "Probably not" — it's the most
     reliable signal we have because the user explicitly listed these
     industries / domains as off-limits.

  2. **Salary floor.** If the JD has a ``salary_max`` and it's below the
     profile's floor (same currency), that's a strong negative signal.
     A salary clearly above floor is a small positive.

  3. **Location preference.** Mismatches between profile's
     ``location_preference`` ("remote-only") and the JD's ``work_type``
     are negative. Matches are positive.

  4. **Keyword overlap.** Profile's ``top_skills`` and ``target_role``
     looked up as substrings in the JD text. The smooth scoring
     component when no hard rule fires.

Confidence is capped at **0.5** for the soft-scoring path because
keyword overlap is noisy. Hard checks (deal-breakers, clearly-below-floor
salary) raise confidence to ~0.6 — those rules are reliable enough that
we should be more sure of "Probably not" than of any soft yes/no.
"""

from __future__ import annotations

from ..config import Profile
from ..models import EvaluationInput, Job
from ..signals import SIGNAL_LABELS, signal_label_for

# Confidence ceiling for the smooth-scoring path. Heuristics are noisy by
# definition — we shouldn't claim more certainty than we can back up. AI
# enrichment in M4 raises the ceiling when it agrees with us.
HEURISTIC_CONFIDENCE_CAP = 0.50

# Higher confidence when a hard rule fires. Deal-breakers are explicit
# user input, so we trust them more than smooth scoring.
HARD_RULE_CONFIDENCE = 0.60

# Minimum confidence for the soft path when the profile is sparse
# (e.g. no top_skills, no target_role). We have very little evidence;
# below this floor signal_label_for routes us to "Need more info".
SPARSE_PROFILE_CONFIDENCE = 0.20

# Score weights for the soft path. Sum should equal 1.0; tweak in tandem.
_SKILL_WEIGHT = 0.60
_ROLE_WEIGHT = 0.40


def _job_text(job: Job) -> str:
    """Concatenated lowercase haystack for substring matching."""
    parts = [
        job.company,
        job.role,
        job.location or "",
        job.raw_content or "",
    ]
    return " ".join(parts).lower()


def _matched_deal_breakers(profile: Profile, haystack: str) -> list[str]:
    """Substring-match each (already-lowercased) deal-breaker tag.

    profile.deal_breakers were normalized to lowercase + stripped at
    persistence time (see config.Profile validator), so we can compare
    directly.
    """
    return [d for d in profile.deal_breakers if d and d in haystack]


def _matched_skills(profile: Profile, haystack: str) -> tuple[list[str], list[str]]:
    """Return (matched, missing) skill tags."""
    matched: list[str] = []
    missing: list[str] = []
    for skill in profile.top_skills:
        if not skill:
            continue
        (matched if skill in haystack else missing).append(skill)
    return matched, missing


def _salary_signal(profile: Profile, job: Job) -> tuple[str, str] | None:
    """Compare the JD's salary range against the profile floor.

    Returns ``(polarity, message)`` where ``polarity`` is ``"pos"`` or
    ``"neg"``, or ``None`` when either side lacks the data needed.
    Cross-currency comparisons are skipped — we don't carry a conversion
    table in v1.
    """
    if profile.salary_floor is None or job.salary_max is None:
        return None
    if (job.salary_currency or "USD").upper() != (
        profile.salary_floor_currency or "USD"
    ).upper():
        return None  # different currencies, no honest comparison
    if job.salary_max < profile.salary_floor:
        return ("neg", f"Salary ceiling {job.salary_max} below your floor {profile.salary_floor}")
    if job.salary_min is not None and job.salary_min >= profile.salary_floor:
        return ("pos", f"Salary {job.salary_min}+ meets your floor {profile.salary_floor}")
    return None


def _location_signal(profile: Profile, job: Job) -> tuple[str, str] | None:
    """Compare profile location preference against the JD's work_type.

    Recognises a few common forms — we don't NLP this, just match
    obvious tokens.
    """
    pref = (profile.location_preference or "").lower()
    work = (job.work_type or "").lower()
    if not pref or not work:
        return None
    if "remote" in pref and "only" in pref:
        if work == "onsite":
            return ("neg", "Remote-only preference; this role is onsite")
        if work == "remote":
            return ("pos", "Remote-only preference matched")
    return None


class HeuristicEvaluator:
    """Implements :class:`wisp.evaluators.Evaluator` without any AI calls."""

    name: str = "heuristic"

    @property
    def kind(self) -> str:
        return "heuristic"

    def is_available(self) -> bool:
        """Always available — that's the whole point of the heuristic
        evaluator."""
        return True

    def evaluate(
        self,
        job: Job,
        profile: Profile,
        checklist: dict[str, str] | None = None,
    ) -> EvaluationInput:
        del checklist  # heuristic ignores it; checklist feeds composite (M3.6)
        haystack = _job_text(job)

        # --- 1) Deal-breaker hard rule -------------------------------------
        deal_hits = _matched_deal_breakers(profile, haystack)
        if deal_hits:
            return self._deal_breaker_eval(deal_hits)

        # --- 2) Soft scoring: skill + role overlap -------------------------
        matched_skills, missing_skills = _matched_skills(profile, haystack)
        skill_score = (
            len(matched_skills) / max(1, len(profile.top_skills))
            if profile.top_skills
            else 0.5
        )
        role_score = (
            1.0
            if profile.target_role and profile.target_role.lower() in haystack
            else 0.0
        )
        fit_score = _SKILL_WEIGHT * skill_score + _ROLE_WEIGHT * role_score

        # --- 3) Salary + location adjustments ------------------------------
        strengths: list[str] = []
        concerns: list[str] = []
        gaps: list[str] = [f"Skill not mentioned in JD: {s}" for s in missing_skills]

        if matched_skills:
            strengths.append(f"Matched skills: {', '.join(matched_skills)}")
        if role_score:
            strengths.append(f"Target role {profile.target_role!r} appears in JD")

        sal = _salary_signal(profile, job)
        if sal is not None:
            polarity, msg = sal
            if polarity == "neg":
                concerns.append(msg)
                fit_score = min(fit_score, 0.30)  # hard penalty
            else:
                strengths.append(msg)

        loc = _location_signal(profile, job)
        if loc is not None:
            polarity, msg = loc
            if polarity == "neg":
                concerns.append(msg)
                fit_score = min(fit_score, 0.30)
            else:
                strengths.append(msg)

        # --- 4) Confidence: cap, modulated by profile / data sparsity ------
        if not profile.top_skills and not profile.target_role:
            confidence = SPARSE_PROFILE_CONFIDENCE
        else:
            # More populated profile → more confidence (still capped).
            populated = sum(
                1 for x in (profile.top_skills, profile.target_role) if x
            )
            confidence = min(
                HEURISTIC_CONFIDENCE_CAP,
                SPARSE_PROFILE_CONFIDENCE + 0.15 * populated,
            )

        signal, label = signal_label_for(fit_score, confidence)
        brief, reasons = self._brief_for(signal, strengths, concerns, gaps)

        return EvaluationInput(
            kind="heuristic",
            fit_score=fit_score,
            confidence=confidence,
            signal=signal,
            signal_label=label,
            brief_recommendation=brief,
            brief_reasons=reasons,
            strengths=strengths,
            gaps=gaps,
            concerns=concerns,
        )

    # ---- Helpers --------------------------------------------------------

    @staticmethod
    def _deal_breaker_eval(deal_hits: list[str]) -> EvaluationInput:
        first = deal_hits[0]
        return EvaluationInput(
            kind="heuristic",
            fit_score=0.0,
            confidence=HARD_RULE_CONFIDENCE,
            signal="no",
            signal_label=SIGNAL_LABELS["no"],
            brief_recommendation=(
                f"This hits your deal-breaker: {first}. I'd skip it."
            ),
            brief_reasons=[f"Deal-breaker matched: {first}"],
            concerns=[f"Deal-breaker matched: {h}" for h in deal_hits],
        )

    @staticmethod
    def _brief_for(
        signal: str,
        strengths: list[str],
        concerns: list[str],
        gaps: list[str],
    ) -> tuple[str, list[str]]:
        """Build (brief_recommendation, brief_reasons[≤2]) from collected
        positive / negative reasons. Tone is advisory: 'I'd lean…',
        not 'You should…'. Verdict text length stays under 140 chars."""
        # Pick the strongest two reasons across polarities to surface in
        # the hot brief. Concerns weigh heavier than gaps; strengths are
        # the positive counterweight.
        reasons: list[str] = []
        if concerns:
            reasons.append(concerns[0])
        if strengths and len(reasons) < 2:
            reasons.append(strengths[0])
        if not reasons and gaps:
            reasons.append(gaps[0])
        # Trim to model cap regardless.
        reasons = reasons[:2]

        # Advisory framing per signal — NEVER imperative.
        verb_by_signal = {
            "yes": "I'd lean apply",
            "stretch": "I'd take a closer look",
            "maybe": "I'm on the fence",
            "no": "I'd lean skip",
            "pending": "I don't have enough evidence yet",
        }
        verb = verb_by_signal.get(signal, "My read is")
        if reasons:
            brief = f"{verb} — {reasons[0]}."
        else:
            brief = f"{verb}, though I don't have much to go on yet."
        # Cap at 140 chars (matches BRIEF_RECOMMENDATION_MAX_LENGTH).
        if len(brief) > 140:
            brief = brief[:137] + "..."
        return brief, reasons
