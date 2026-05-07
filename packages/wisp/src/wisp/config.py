"""Persistent configuration: profile, AI keys, user-data paths.

The on-disk shape is JSON at ``<user_data_dir>/config.json``. Fields are
intentionally optional so the file can be written before the setup wizard
(M7) finishes; ``is_first_run()`` keys off whether ``profile`` is set.

Set ``WISP_DATA_DIR`` to override the user-data directory (useful for tests
and ad-hoc dev runs).

Failure modes are surfaced through :class:`WispConfigError` so callers can
present a useful message to the user instead of a raw stack trace. Three
classes of failure are distinguished:

* the data directory cannot be created or written to;
* the config file exists but is unreadable or not valid JSON;
* the config file is valid JSON but doesn't match the schema.

A missing config file is *not* an error — it just means first run.
"""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path

from platformdirs import user_data_dir
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

APP_NAME = "wisp"
CONFIG_FILENAME = "config.json"
DB_FILENAME = "wisp.db"
LOG_FILENAME = "wisp.log"

# Tolerate unknown fields when loading older/newer config files.
# The setup wizard owns the schema; the loader should never be the thing
# that breaks an upgrade. ``schema_version`` carries an integer we can use
# to drive explicit migrations later.
_TOLERANT = ConfigDict(extra="ignore")

# data_dir() ensures the directory exists. We only need to do that once per
# unique path per process — repeated mkdir calls are wasteful and the comment
# from the PR review pointed it out. The set of paths already initialized is
# small (usually one) and the lookup is cheap. Tests that monkeypatch
# WISP_DATA_DIR get a fresh path so they pass through the mkdir branch.
_initialized_data_dirs: set[Path] = set()


class WispConfigError(RuntimeError):
    """Raised when Wisp config can't be read, parsed, or written.

    Distinct from missing-config (which is just first run) and from generic
    ``OSError``/``ValueError`` so callers can present a clear, recoverable
    message to the user.
    """


def data_dir() -> Path:
    """Return the directory where Wisp stores config, DB, and logs.

    Creates it on first use per process. Subsequent calls don't re-mkdir.
    Raises :class:`WispConfigError` with an actionable message if the
    directory cannot be created (permission denied, read-only filesystem,
    parent doesn't exist, etc.).
    """
    override = os.environ.get("WISP_DATA_DIR")
    if override:
        path = Path(override).expanduser()
    else:
        # appauthor=False prevents an extra "Wisp" intermediate dir on Windows
        path = Path(user_data_dir(APP_NAME, appauthor=False))
    if path not in _initialized_data_dirs:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise WispConfigError(
                f"Cannot create Wisp data directory at {path}: "
                f"{exc.strerror or exc}. Set WISP_DATA_DIR to a writable "
                f"location, or fix the permissions on this one."
            ) from exc
        _initialized_data_dirs.add(path)
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
    """Read the config file, returning a fresh ``Config`` if it doesn't exist.

    Raises :class:`WispConfigError` if the file exists but is unreadable,
    not valid JSON, or doesn't match the schema. Distinguishing these from
    "no config yet" lets the caller treat a corrupt file as a recoverable
    user-facing problem rather than silently re-running the setup wizard.
    """
    path = config_path()
    _cleanup_stale_tmp(path)
    if not path.exists():
        return Config()
    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except OSError as exc:
        raise WispConfigError(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise WispConfigError(
            f"Config file {path} is not valid JSON: {exc.msg} (line {exc.lineno}). "
            f"Edit or delete the file to recover."
        ) from exc
    try:
        return Config.model_validate(raw)
    except ValidationError as exc:
        raise WispConfigError(
            f"Config file {path} has an invalid structure ({exc.error_count()} "
            f"error(s)). Fix it manually, or delete it to start over."
        ) from exc


def save(config: Config) -> None:
    """Atomically persist ``config`` to disk.

    Crash-safe across both process death and (on platforms that honor it)
    power loss: data is fully written and ``fsync``-ed before the rename so
    the directory entry never points at a file with no contents. The
    rename itself is atomic on POSIX and on NTFS via ``os.replace``.
    """
    path = config_path()
    tmp = path.with_suffix(".json.tmp")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(path)
    except OSError as exc:
        # Best-effort cleanup of the partial tmp file so the next load()
        # doesn't have to.
        with contextlib.suppress(OSError):
            tmp.unlink()
        raise WispConfigError(f"Cannot write {path}: {exc}") from exc


def is_first_run() -> bool:
    """True if no config file exists yet, or it exists but has no profile.

    A *corrupt* config file is **not** treated as a first run — it raises
    :class:`WispConfigError` (via ``load()``) so the caller can show the
    user something useful instead of silently re-running setup and
    overwriting their broken-but-recoverable config.
    """
    if not config_path().exists():
        return True
    cfg = load()  # may raise WispConfigError; that's the point
    return cfg.profile is None
