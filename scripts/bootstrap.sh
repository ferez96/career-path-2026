#!/usr/bin/env bash
# Bootstrap local working files from templates. Run from repo root:
#   bash scripts/bootstrap.sh
# Safe to re-run: skips targets that already exist (no overwrite).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

copy_if_missing() {
  local src="$1" dest="$2"
  if [[ ! -f "$dest" ]]; then
    cp "$src" "$dest"
    echo "Created $dest"
  else
    echo "Skip (exists): $dest"
  fi
}

mkdir -p \
  "$ROOT/data/private" \
  "$ROOT/data/raw" \
  "$ROOT/data/weekly" \
  "$ROOT/data/daily" \
  "$ROOT/reports/private" \
  "$ROOT/reports/benchmarks" \
  "$ROOT/reports/briefs"

copy_if_missing "$ROOT/templates/opportunities_tracker_template.yaml" "$ROOT/data/private/opportunities.yaml"
copy_if_missing "$ROOT/templates/master_template.yaml" "$ROOT/data/private/master.yaml"
copy_if_missing "$ROOT/templates/jd_catalog_template.csv" "$ROOT/config/jd_catalog.csv"
copy_if_missing "$ROOT/templates/weekly_plan_template.md" "$ROOT/data/weekly/weekly-plan-TEMPLATE.md"
copy_if_missing "$ROOT/templates/daily_review_template.md" "$ROOT/data/daily/daily-review-TEMPLATE.md"

echo "Done."
