"""Shared domain types for token and cost tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class UsageEvent:
    """A single tracked LLM request."""

    ts: datetime
    task_type: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    duration_ms: int
    source: str
    status: str
    request_id: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UsageCost:
    """Computed cost for a usage event."""

    input_cost: float
    output_cost: float
    cached_cost: float
    total_cost: float
    currency: str = "USD"

