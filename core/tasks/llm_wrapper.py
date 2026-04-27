"""Provider-agnostic chat wrapper with telemetry."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from adapters.llm.openai_adapter import OpenAIAdapter
from adapters.telemetry.usage_logger import UsageLogger
from core.tasks.file_context import (
    LocalFileContextLoader,
    build_file_context_message,
)
from core.types import UsageEvent


class LLMChatWrapper:
    """Routes chat requests and records metrics in one place."""

    def __init__(self, usage_logger: UsageLogger) -> None:
        self.usage_logger = usage_logger
        self._repo_root = Path(__file__).resolve().parents[2]
        self._file_loader = LocalFileContextLoader(self._repo_root)

    def chat(
        self,
        *,
        task_type: str,
        provider: str,
        model: str,
        messages: list[dict[str, Any]],
        attached_paths: list[str] | None = None,
        source: str = "manual_logs",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        start = perf_counter()
        metadata = metadata or {}
        loader_result = self._file_loader.load_paths(attached_paths)
        context_message = build_file_context_message(loader_result)
        model_messages = messages
        if context_message:
            model_messages = [{"role": "system", "content": context_message}, *messages]
        metadata = {
            **metadata,
            "attached_paths": [item.path for item in loader_result.loaded],
            "attached_files_count": len(loader_result.loaded),
            "attached_skipped_count": len(loader_result.skipped),
            "attached_included_chars": loader_result.included_chars,
            "attached_skipped": [
                {"path": item.path, "reason": item.reason} for item in loader_result.skipped
            ],
        }
        try:
            if provider != "openai":
                raise ValueError(f"Unsupported provider for MVP: {provider}")
            response = OpenAIAdapter().chat(model=model, messages=model_messages)
            duration_ms = int((perf_counter() - start) * 1000)

            usage = response["usage"]
            event = UsageEvent(
                ts=datetime.now(timezone.utc),
                task_type=task_type,
                provider=provider,
                model=model,
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                cached_tokens=usage["cached_tokens"],
                duration_ms=duration_ms,
                source=source,
                status="success",
                request_id=response.get("request_id"),
                metadata=metadata,
            )
            usage_cost = self.usage_logger.log_event(event)
            return {
                "request_id": response.get("request_id"),
                "content": response.get("content", ""),
                "attachments": {
                    "loaded": [item.path for item in loader_result.loaded],
                    "skipped": [
                        {"path": item.path, "reason": item.reason}
                        for item in loader_result.skipped
                    ],
                    "included_chars": loader_result.included_chars,
                },
                "usage": {
                    **usage,
                    "cost_input": round(usage_cost.input_cost, 8),
                    "cost_output": round(usage_cost.output_cost, 8),
                    "cost_cached": round(usage_cost.cached_cost, 8),
                    "cost_total": round(usage_cost.total_cost, 8),
                    "currency": usage_cost.currency,
                    "duration_ms": duration_ms,
                },
            }
        except Exception as exc:
            duration_ms = int((perf_counter() - start) * 1000)
            self.usage_logger.log_error_event(
                task_type=task_type,
                provider=provider,
                model=model,
                source=source,
                duration_ms=duration_ms,
                request_id=None,
                error_message=str(exc),
                metadata=metadata,
            )
            raise

