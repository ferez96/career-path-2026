"""Flask + HTMX + Bootstrap web UI for token monitor."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from apps.runtime import build_runtime
from core.tasks.file_context import parse_attached_paths


REPOSITORY, _USAGE_LOGGER, WRAPPER = build_runtime()
app = Flask(__name__, template_folder="templates")


def current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _offset_month(month: str, delta: int) -> str:
    year, m = int(month[:4]), int(month[5:7])
    m += delta
    while m > 12:
        m -= 12
        year += 1
    while m < 1:
        m += 12
        year -= 1
    return f"{year:04d}-{m:02d}"


def get_monthly_metrics(month: str) -> dict:
    breakdown = REPOSITORY.monthly_breakdown(month)
    total_cost = sum(row["total_cost"] for row in breakdown)
    total_requests = sum(row["requests"] for row in breakdown)
    return {
        "month": month,
        "total_cost": round(total_cost, 8),
        "total_requests": total_requests,
        "breakdown": breakdown,
        "alerts": REPOSITORY.open_alerts(month),
        "recent_usage": REPOSITORY.recent_usage(limit=20),
    }


def dashboard_context(month: str) -> dict:
    metrics = get_monthly_metrics(month)
    return {
        "month": month,
        "prev_month": _offset_month(month, -1),
        "next_month": _offset_month(month, +1),
        "metrics": metrics,
    }


@app.get("/")
def index() -> str:
    month = request.args.get("month", current_month())
    return render_template("index.html", **dashboard_context(month))


@app.get("/partials/dashboard")
def dashboard_partial() -> str:
    month = request.args.get("month", current_month())
    return render_template("partials/dashboard.html", **dashboard_context(month))


@app.post("/partials/chat")
def chat_partial() -> str:
    task_type = request.form.get("task_type", "")
    provider = request.form.get("provider", "openai")
    model = request.form.get("model", "")
    prompt = request.form.get("prompt", "")
    source = request.form.get("source", "manual_logs")
    attached_paths = parse_attached_paths(request.form.get("attached_paths", ""))

    if not task_type or not model or not prompt:
        return render_template(
            "partials/chat_result.html",
            error="task_type, model, and prompt are required.",
            content="",
            usage=None,
            attachments={},
        )

    try:
        result = WRAPPER.chat(
            task_type=task_type,
            provider=provider,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            attached_paths=attached_paths,
            source=source,
            metadata={},
        )
        return render_template(
            "partials/chat_result.html",
            content=result.get("content", ""),
            usage=result.get("usage"),
            attachments=result.get("attachments", {}),
            error=None,
        )
    except Exception as exc:  # pragma: no cover
        return render_template(
            "partials/chat_result.html",
            error=f"Request failed: {exc}",
            content="",
            usage=None,
            attachments={},
        )


@app.get("/api/metrics/monthly")
def monthly_metrics():
    month = request.args.get("month", current_month())
    return jsonify(get_monthly_metrics(month))


@app.post("/api/llm/chat")
def chat_api():
    payload = request.get_json(silent=True) or {}
    required = ["task_type", "provider", "model", "messages"]
    missing = [name for name in required if name not in payload]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    attached_paths: list[str]
    raw_paths = payload.get("attached_paths", [])
    if isinstance(raw_paths, str):
        attached_paths = parse_attached_paths(raw_paths)
    elif isinstance(raw_paths, list):
        attached_paths = [str(item).strip() for item in raw_paths if str(item).strip()]
    else:
        attached_paths = []

    try:
        result = WRAPPER.chat(
            task_type=payload["task_type"],
            provider=payload["provider"],
            model=payload["model"],
            messages=payload["messages"],
            attached_paths=attached_paths,
            source=payload.get("source", "manual_logs"),
            metadata=payload.get("metadata", {}),
        )
        return jsonify(result), 200
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": str(exc)}), 502


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Flask token monitor web server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.reload, use_reloader=args.reload)


if __name__ == "__main__":
    main()

