param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("init-db", "run-web", "run-web-dev", "refresh-rollups", "monthly", "alerts")]
  [string]$Command,
  [string]$Month = ""
)

$root = Split-Path -Parent $PSScriptRoot

switch ($Command) {
  "init-db" {
    python -m apps.cli.main init-db
  }
  "run-web" {
    python -m apps.web.flask_server --host 127.0.0.1 --port 8000
  }
  "run-web-dev" {
    python -m apps.web.flask_server --host 127.0.0.1 --port 8000 --reload
  }
  "refresh-rollups" {
    python -m apps.cli.main refresh-rollups
  }
  "monthly" {
    if ([string]::IsNullOrWhiteSpace($Month)) {
      python -m apps.cli.main monthly
    } else {
      python -m apps.cli.main monthly --month $Month
    }
  }
  "alerts" {
    if ([string]::IsNullOrWhiteSpace($Month)) {
      python -m apps.cli.main alerts
    } else {
      python -m apps.cli.main alerts --month $Month
    }
  }
}

