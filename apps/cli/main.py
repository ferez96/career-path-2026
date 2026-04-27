"""CLI for token usage monitoring operations."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from apps.runtime import build_runtime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Token monitor CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Ensure SQLite schema exists")
    sub.add_parser("refresh-rollups", help="Recompute monthly rollups from raw events")

    month_parser = sub.add_parser("monthly", help="Show monthly summary")
    month_parser.add_argument("--month", default=datetime.now(timezone.utc).strftime("%Y-%m"))

    alert_parser = sub.add_parser("alerts", help="Show open alerts")
    alert_parser.add_argument("--month", default=None)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository, _logger, _wrapper = build_runtime()
    try:
        if args.command == "init-db":
            print(f"DB ready at {repository.db_path}")
            return
        if args.command == "refresh-rollups":
            repository.recompute_monthly_rollups()
            print("Monthly rollups refreshed.")
            return
        if args.command == "monthly":
            rows = repository.monthly_breakdown(args.month)
            payload = {
                "month": args.month,
                "total_cost": round(sum(row["total_cost"] for row in rows), 8),
                "total_requests": sum(row["requests"] for row in rows),
                "breakdown": rows,
            }
            print(json.dumps(payload, indent=2))
            return
        if args.command == "alerts":
            print(json.dumps(repository.open_alerts(args.month), indent=2))
            return
    finally:
        repository.close()


if __name__ == "__main__":
    main()

