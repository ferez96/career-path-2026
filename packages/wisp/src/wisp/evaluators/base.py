"""Evaluator Protocol.

An evaluator reads a :class:`Job` (already persisted by the adapter), a
:class:`Profile` (the user's calibration data), and an optional decision
checklist (``{item_key: value}``), and emits an
:class:`EvaluationInput` ready to be persisted via
:meth:`VaultAdapter.add_evaluation`.

The Protocol does not promise any specific run cost. Heuristic
implementations are pure-Python and finish in microseconds; AI-backed
ones may make a network call. Routes / composite mergers should treat
the call as potentially blocking and surface progress to the user
accordingly.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..config import Profile
from ..models import EvaluationInput, EvaluationKind, Job


@runtime_checkable
class Evaluator(Protocol):
    """Reads a Job + Profile + optional checklist, emits an
    :class:`EvaluationInput`.

    Implementations must:
      * be safe to call multiple times for the same inputs (idempotent
        for the same data — different calls may produce different
        outputs if e.g. the AI backend is non-deterministic);
      * produce ``kind`` matching the ``kind`` attribute below;
      * cap their own ``confidence`` honestly — heuristic implementations
        max out at 0.5 by design, AI implementations should cap below
        1.0 to leave room for composite agreement boost.
    """

    @property
    def name(self) -> str:
        """Human-readable identifier ('heuristic', 'anthropic', etc.)
        used in logs and the timeline event detail."""

    @property
    def kind(self) -> EvaluationKind:
        """Either 'heuristic' or 'ai' — drives the composite merge.
        Never 'composite'; the composite row is built by
        :mod:`wisp.evaluators.composite`, not by an Evaluator."""

    def is_available(self) -> bool:
        """``True`` if this evaluator can run right now.

        Heuristic implementations always return ``True``. AI
        implementations check that a backend (API key, CLI binary) is
        configured before reporting True. The composite merger asks
        each evaluator before invoking ``evaluate``.
        """

    def evaluate(
        self,
        job: Job,
        profile: Profile,
        checklist: dict[str, str] | None = None,
    ) -> EvaluationInput:
        """Run the evaluator and emit a fresh ``EvaluationInput`` row.

        ``checklist`` may be empty / None on first run; AI-backed
        evaluators can include a "user has self-rated these dimensions"
        prompt section when present.
        """
