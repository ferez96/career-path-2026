"""Token cost calculation."""

from __future__ import annotations

from core.cost.pricing import ModelPricing
from core.types import UsageCost


def _to_cost(tokens: int, rate_per_1k: float) -> float:
    return (max(tokens, 0) / 1000.0) * rate_per_1k


def calculate_usage_cost(
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    pricing: ModelPricing,
) -> UsageCost:
    input_cost = _to_cost(input_tokens, pricing.input_per_1k)
    output_cost = _to_cost(output_tokens, pricing.output_per_1k)
    cached_cost = _to_cost(cached_tokens, pricing.cached_input_per_1k)
    total_cost = input_cost + output_cost + cached_cost
    return UsageCost(
        input_cost=input_cost,
        output_cost=output_cost,
        cached_cost=cached_cost,
        total_cost=total_cost,
        currency=pricing.currency,
    )

