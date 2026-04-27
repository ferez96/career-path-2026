"""Usage logger to persist events and evaluate monthly budget alerts."""

from __future__ import annotations

from datetime import datetime, timezone

from adapters.storage.sqlite.repository import TokenUsageRepository
from core.cost.budget import BudgetPolicy, evaluate_alert
from core.cost.costing import calculate_usage_cost
from core.cost.pricing import PricingCatalog
from core.types import UsageEvent, UsageCost


class UsageLogger:
    """Coordinates cost computation, event persistence, and alert checks."""

    def __init__(
        self,
        repository: TokenUsageRepository,
        pricing_catalog: PricingCatalog,
        budget_policy: BudgetPolicy,
    ) -> None:
        self.repository = repository
        self.pricing_catalog = pricing_catalog
        self.budget_policy = budget_policy

    def log_event(self, event: UsageEvent) -> UsageCost:
        pricing = self.pricing_catalog.resolve(event.provider, event.model)
        usage_cost = calculate_usage_cost(
            input_tokens=event.input_tokens,
            output_tokens=event.output_tokens,
            cached_tokens=event.cached_tokens,
            pricing=pricing,
        )
        self.repository.insert_usage_event(event=event, total_cost=usage_cost.total_cost)
        self._evaluate_monthly_alerts(event.ts.strftime("%Y-%m"))
        return usage_cost

    def log_error_event(
        self,
        *,
        task_type: str,
        provider: str,
        model: str,
        source: str,
        duration_ms: int,
        request_id: str | None,
        error_message: str,
        metadata: dict | None = None,
    ) -> None:
        event = UsageEvent(
            ts=datetime.now(timezone.utc),
            task_type=task_type,
            provider=provider,
            model=model,
            input_tokens=0,
            output_tokens=0,
            cached_tokens=0,
            duration_ms=duration_ms,
            source=source,
            status="error",
            request_id=request_id,
            error_message=error_message[:500],
            metadata=metadata or {},
        )
        self.repository.insert_usage_event(event=event, total_cost=0.0)
        self._evaluate_monthly_alerts(event.ts.strftime("%Y-%m"))

    def _evaluate_monthly_alerts(self, month: str) -> None:
        warn_ratio = self.budget_policy.warn_ratio
        global_limit = self.budget_policy.monthly_global_limit
        global_cost = self.repository.get_monthly_total_cost(month)
        global_alert = evaluate_alert(
            month=month,
            scope_type="global",
            scope_value="all",
            current_usd=global_cost,
            limit_usd=global_limit,
            warn_ratio=warn_ratio,
        )
        if global_alert:
            self.repository.upsert_alert(global_alert)

        for task_type, limit in self.budget_policy.monthly_task_limits.items():
            task_cost = self.repository.get_monthly_task_cost(month, task_type)
            task_alert = evaluate_alert(
                month=month,
                scope_type="task_type",
                scope_value=task_type,
                current_usd=task_cost,
                limit_usd=limit,
                warn_ratio=warn_ratio,
            )
            if task_alert:
                self.repository.upsert_alert(task_alert)

