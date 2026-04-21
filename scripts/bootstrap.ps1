# Bootstrap local working files from templates. Run from repo root:
#   pwsh -File scripts/bootstrap.ps1
# Safe to re-run: skips targets that already exist (no overwrite).

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Copy-IfMissing {
  param([string]$Source, [string]$Dest)
  if (-not (Test-Path $Dest)) {
    Copy-Item -LiteralPath $Source -Destination $Dest
    Write-Host "Created $Dest"
  }
  else {
    Write-Host "Skip (exists): $Dest"
  }
}

$dirs = @(
  "data/private",
  "data/raw",
  "data/weekly",
  "data/daily",
  "reports/private",
  "reports/benchmarks",
  "reports/briefs"
)
foreach ($d in $dirs) {
  $p = Join-Path $Root $d
  if (-not (Test-Path $p)) {
    New-Item -ItemType Directory -Path $p | Out-Null
    Write-Host "Created directory $d"
  }
}

Copy-IfMissing -Source (Join-Path $Root "templates/opportunities_tracker_template.yaml") -Dest (Join-Path $Root "data/private/opportunities.yaml")
Copy-IfMissing -Source (Join-Path $Root "templates/master_template.yaml") -Dest (Join-Path $Root "data/private/master.yaml")
Copy-IfMissing -Source (Join-Path $Root "templates/jd_catalog_template.csv") -Dest (Join-Path $Root "config/jd_catalog.csv")
Copy-IfMissing -Source (Join-Path $Root "templates/weekly_plan_template.md") -Dest (Join-Path $Root "data/weekly/weekly-plan-TEMPLATE.md")
Copy-IfMissing -Source (Join-Path $Root "templates/daily_review_template.md") -Dest (Join-Path $Root "data/daily/daily-review-TEMPLATE.md")

Write-Host "Done."
