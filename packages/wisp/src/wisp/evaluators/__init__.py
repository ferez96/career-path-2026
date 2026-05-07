"""Evaluators turn (job, profile, checklist) into an :class:`EvaluationInput`.

The :class:`Evaluator` Protocol is satisfied by:
  * :class:`HeuristicEvaluator` — always available, no AI required
  * an AI-backed evaluator wrapping the :mod:`wisp.ai_providers` layer
    (lands in M4)

The :mod:`wisp.evaluators.composite` module merges heuristic + ai
results into a composite row. All three rows (heuristic, ai, composite)
persist via :meth:`SqliteVaultAdapter.add_evaluation` so disagreement
remains auditable.
"""

from .base import Evaluator
from .heuristics import HeuristicEvaluator

__all__ = ["Evaluator", "HeuristicEvaluator"]
