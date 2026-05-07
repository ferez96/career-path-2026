"""Persistent configuration: profile, AI keys, user-data paths.

The on-disk shape is JSON at ``<user_data_dir>/config.json``. Fields are
intentionally optional so the file can be written before the setup wizard
(M7) finishes; ``is_first_run()`` keys off whether ``profile`` is set.

Set ``WISP_DATA_DIR`` to override the user-data directory (useful for tests
and ad-hoc dev runs).
"""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path

from platformdirs import user_data_dir
from pydantic import BaseModel, ConfigDict, Field, field_validator

APP_NAME = "wisp"
CONFIG_FILENAME = "config.json"
DB_FILENAME = "wisp.db"
LOG_FILENAME = "wisp.log"

# Tolerate unknown fields when loading older/newer config files.
# The setup wizard owns the schema; the loader should never be the thing
# that breaks an upgrade. ``schema_version`` carries an integer we can use
# to drive explicit migrations later.
_TOLERANT = ConfigDict(extra="ignore")


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


def _normalize_tag_list(values: list[str]) -> list[str]:
    """Lower-case, strip, drop empties, dedupe while preserving order.

    Used for ``deal_breakers`` and ``top_skills`` so the M3 heuristic can do
    case-insensitive substring matching against JD text without re-normalizing
    on every read.
    """
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        norm = v.strip().lower()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


class Profile(BaseModel):
    """User profile that calibrates the heuristic and AI evaluators."""

    model_config = _TOLERANT

    current_role: str = ""
    target_role: str = ""
    location_preference: str = ""  # e.g. "remote-only", "hybrid SF", "onsite NYC"
    salary_floor: int | None = None  # annualized
    # Currency must accompany the salary floor — without it the heuristic
    # cannot meaningfully compare against parsed JD salaries (USD/VND/SGD/...).
    # ISO 4217 alpha-3 codes; default USD because that's what most JDs we see use.
    salary_floor_currency: str = "USD"
    deal_breakers: list[str] = Field(default_factory=list)  # industries / domains to avoid
    top_skills: list[str] = Field(default_factory=list)

    @field_validator("salary_floor_currency", mode="before")
    @classmethod
    def _upper_currency(cls, v: object) -> object:
        return v.upper() if isinstance(v, str) else v

    @field_validator("deal_breakers", "top_skills", mode="after")
    @classmethod
    def _normalize_tags(cls, v: list[str]) -> list[str]:
        return _normalize_tag_list(v)


class AIKeys(BaseModel):
    """API keys for cloud AI providers. Empty string means unset.

    Stored plaintext under the user-data directory. Acceptable for a
    personal-use desktop app; revisit with OS keychain (``keyring``) before
    shipping a multi-user or hosted form. See plan risks section.
    """

    model_config = _TOLERANT

    anthropic: str = ""
    openai: str = ""
    gemini: str = ""


class Config(BaseModel):
    """Persistent application config."""

    model_config = _TOLERANT

    schema_version: int = 1
    profile: Profile | None = None
    ai_keys: AIKeys = Field(default_factory=AIKeys)


def _cleanup_stale_tmp(path: Path) -> None:
    """Remove a leftover ``.tmp`` from a previous interrupted save, if any."""
    tmp = path.with_suffix(".json.tmp")
    if tmp.exists():
        # Best-effort; not worth crashing for a stray temp file.
        with contextlib.suppress(OSError):
            tmp.unlink()


def load() -> Config:
    """Read the config file, returning a fresh ``Config`` if it doesn't exist."""
    path = config_path()
    _cleanup_stale_tmp(path)
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
