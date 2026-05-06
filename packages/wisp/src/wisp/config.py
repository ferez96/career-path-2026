"""Persistent configuration: profile, AI keys, user-data paths.

The on-disk shape is JSON at ``<user_data_dir>/config.json``. Fields are
intentionally optional so the file can be written before the setup wizard
(M7) finishes; ``is_first_run()`` keys off whether ``profile`` is set.

Set ``WISP_DATA_DIR`` to override the user-data directory (useful for tests
and ad-hoc dev runs).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from platformdirs import user_data_dir
from pydantic import BaseModel, Field

APP_NAME = "wisp"
CONFIG_FILENAME = "config.json"
DB_FILENAME = "wisp.db"
LOG_FILENAME = "wisp.log"


def data_dir() -> Path:
    """Return the directory where Wisp stores config, DB, and logs."""
    override = os.environ.get("WISP_DATA_DIR")
    if override:
        path = Path(override).expanduser()
    else:
        # appauthor=False prevents an extra "Wisp" intermediate dir on Windows
        path = Path(user_data_dir(APP_NAME, appauthor=False))
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return data_dir() / CONFIG_FILENAME


def db_path() -> Path:
    return data_dir() / DB_FILENAME


def log_path() -> Path:
    return data_dir() / LOG_FILENAME


class Profile(BaseModel):
    """User profile that calibrates the heuristic and AI evaluators."""

    current_role: str = ""
    target_role: str = ""
    location_preference: str = ""  # e.g. "remote-only", "hybrid SF", "onsite NYC"
    salary_floor: int | None = None  # annualized; currency assumed to match JD
    deal_breakers: list[str] = Field(default_factory=list)  # industries / domains to avoid
    top_skills: list[str] = Field(default_factory=list)


class AIKeys(BaseModel):
    """API keys for cloud AI providers. Empty string means unset."""

    anthropic: str = ""
    openai: str = ""
    gemini: str = ""


class Config(BaseModel):
    """Persistent application config."""

    schema_version: int = 1
    profile: Profile | None = None
    ai_keys: AIKeys = Field(default_factory=AIKeys)


def load() -> Config:
    """Read the config file, returning a fresh ``Config`` if it doesn't exist."""
    path = config_path()
    if not path.exists():
        return Config()
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return Config.model_validate(raw)


def save(config: Config) -> None:
    """Atomically persist ``config`` to disk."""
    path = config_path()
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2, sort_keys=True)
    tmp.replace(path)


def is_first_run() -> bool:
    """True if the user hasn't completed the setup wizard yet.

    Keying on ``profile is None`` lets us write partial config (e.g. AI keys
    set during a migration) without flipping out of first-run mode.
    """
    cfg = load()
    return cfg.profile is None
