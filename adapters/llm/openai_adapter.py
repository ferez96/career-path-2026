"""OpenAI Responses API adapter."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class OpenAIAdapter:
    """Minimal OpenAI client based on the Responses API."""

    def __init__(self, api_key: str | None = None, timeout_seconds: int = 60) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI adapter")
        self.timeout_seconds = timeout_seconds

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = json.dumps(
            {
                "model": model,
                "input": messages,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url="https://api.openai.com/v1/responses",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"OpenAI API error: {exc.code} {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI API connection error: {exc}") from exc

        parsed = json.loads(response_body)
        return {
            "request_id": parsed.get("id"),
            "content": self._extract_text(parsed),
            "usage": self._extract_usage(parsed),
            "raw": parsed,
        }

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        output_text = payload.get("output_text")
        if isinstance(output_text, str):
            return output_text

        # Fallback if output_text is unavailable.
        chunks: list[str] = []
        for item in payload.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"} and content.get("text"):
                    chunks.append(content["text"])
        return "\n".join(chunks).strip()

    @staticmethod
    def _extract_usage(payload: dict[str, Any]) -> dict[str, int]:
        usage = payload.get("usage", {}) or {}
        input_tokens = int(usage.get("input_tokens", 0))
        output_tokens = int(usage.get("output_tokens", 0))
        cached_tokens = int(
            usage.get("input_tokens_details", {}).get("cached_tokens", 0)
        )
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
        }

