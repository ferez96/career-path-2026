"""Monthly budget evaluation logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - surfaced at runtime
    raise RuntimeError(
        "Missing dependency 'PyYAML'. Install with: pip install pyyaml"
    ) from exc


@dataclass(slots=True)
class BudgetAlert:
    """Alert payload for monthly budget threshold."""

    month: str
    scope_type: str
    scope_value: str
    limit_usd: float
    current_usd: float
    severity: str
    status: str
    triggered_at: str


class BudgetPolicy:
    """Loads monthly budget policies from YAML."""

    def __init__(self, budget_file: Path) -> None:
        self._budget_file = budget_file
        self._raw = self._load()

    def _load(self) -> dict[str, Any]:
        if not self._budget_file.exists():
            raise FileNotFoundError(f"Budget config not found: {self._budget_file}")
        with self._budget_file.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if "monthly" not in data:
            raise ValueError("Invalid budget config: missing top-level 'monthly'")
        return data

    def refresh(self) -> None:
        self._raw = self._load()

    @property
    def warn_ratio(self) -> float:
        return float(self._raw.get("warn_ratio", 0.8))

    @property
    def monthly_global_limit(self) -> float:
        monthly = self._raw.get("monthly", {})
        return float(monthly.get("global_limit_usd", 0.0))

    def monthly_task_limit(self, task_type: str) -> float | None:
        task_limits = self._raw.get("monthly", {}).get("task_limits_usd", {})
        value = task_limits.get(task_type)
        return float(value) if value is not None else None

    @property
    def monthly_task_limits(self) -> dict[str, float]:
        task_limits = self._raw.get("monthly", {}).get("task_limits_usd", {})
        return {name: float(value) for name, value in task_limits.items()}


def evaluate_alert(
    month: str,
    scope_type: str,
    scope_value: str,
    current_usd: float,
    limit_usd: float,
    warn_ratio: float,
) -> BudgetAlert | None:
    if limit_usd <= 0:
        return None
    if current_usd < limit_usd * warn_ratio:
        return None
    severity = "critical" if current_usd >= limit_usd else "warning"
    return BudgetAlert(
        month=month,
        scope_type=scope_type,
        scope_value=scope_value,
        limit_usd=limit_usd,
        current_usd=current_usd,
        severity=severity,
        status="open",
        triggered_at=datetime.now(timezone.utc).isoformat(),
    )

