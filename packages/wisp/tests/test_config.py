"""Tests for ``wisp.config`` — round-trip, first-run, schema drift, normalization,
crash-safety, and error reporting."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from wisp import config
from wisp.config import AIKeys, Config, Profile, WispConfigError


def test_first_run_on_empty_dir() -> None:
    assert config.is_first_run() is True
    cfg = config.load()
    assert cfg.profile is None
    assert cfg.ai_keys.anthropic == ""


def test_save_and_load_roundtrip() -> None:
    cfg = Config(
        profile=Profile(
            current_role="Senior UX Designer",
            target_role="Staff Product Designer",
            location_preference="remote-only",
            salary_floor=120_000,
            salary_floor_currency="usd",  # case-insensitive on input
            deal_breakers=["Finance", "Gambling", "finance"],  # dupes / case
            top_skills=["Design Systems", " prototyping "],  # whitespace
        ),
        ai_keys=AIKeys(anthropic="sk-test-XXXX"),
    )
    config.save(cfg)
    assert config.is_first_run() is False

    reloaded = config.load()
    assert reloaded.profile is not None
    assert reloaded.profile.salary_floor == 120_000
    assert reloaded.profile.salary_floor_currency == "USD"
    # normalized: lowercased, stripped, deduped, order preserved
    assert reloaded.profile.deal_breakers == ["finance", "gambling"]
    assert reloaded.profile.top_skills == ["design systems", "prototyping"]
    assert reloaded.ai_keys.anthropic == "sk-test-XXXX"


def test_on_disk_shape_is_pretty_json() -> None:
    config.save(Config(profile=Profile(target_role="x")))
    raw = config.config_path().read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert parsed["schema_version"] == 1
    assert parsed["profile"]["target_role"] == "x"
    # sort_keys + indent gives stable diffs
    assert "\n" in raw and raw.startswith("{\n")


def test_deleting_config_resets_first_run() -> None:
    config.save(Config(profile=Profile(target_role="x")))
    assert config.is_first_run() is False
    config.config_path().unlink()
    assert config.is_first_run() is True


def test_data_dir_uses_env_override(isolated_wisp_data_dir: Path) -> None:
    assert isolated_wisp_data_dir.resolve() == config.data_dir().resolve()
    assert config.db_path().name == "wisp.db"
    assert config.log_path().name == "wisp.log"


def test_unknown_fields_are_ignored_for_forward_compat() -> None:
    """A newer Wisp wrote fields we don't know yet — load must not crash."""
    config.config_path().write_text(
        json.dumps(
            {
                "schema_version": 99,
                "profile": {
                    "current_role": "x",
                    "target_role": "y",
                    "favourite_colour": "puce",  # unknown
                },
                "ai_keys": {"anthropic": "k", "future_provider": "z"},  # unknown
                "experimental_feature_flags": ["foo"],  # unknown
            }
        ),
        encoding="utf-8",
    )
    cfg = config.load()
    assert cfg.profile is not None
    assert cfg.profile.current_role == "x"
    assert cfg.ai_keys.anthropic == "k"


def test_stale_tmp_file_is_cleaned_on_load() -> None:
    """A crash mid-save can leave a config.json.tmp; load() must clean it."""
    stale = config.config_path().with_suffix(".json.tmp")
    stale.write_text("{stale_garbage", encoding="utf-8")
    assert stale.exists()
    config.load()  # should not raise
    assert not stale.exists()


# ---- New tests for the PR-review fixes ------------------------------------


def test_data_dir_mkdir_runs_at_most_once_per_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Repeated data_dir() calls must not call mkdir again for the same path.

    Addresses PR#17 review comment: "multiple call data_dir() trigger
    multiple mkdir? This is not necessary."
    """
    # Force a fresh path the cache hasn't seen
    fresh = tmp_path / "fresh-data-dir"
    monkeypatch.setenv("WISP_DATA_DIR", str(fresh))

    calls: list[Path] = []
    real_mkdir = Path.mkdir

    def counting_mkdir(self: Path, *args: object, **kwargs: object) -> None:
        calls.append(self)
        real_mkdir(self, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "mkdir", counting_mkdir)

    config.data_dir()
    config.data_dir()
    config.data_dir()
    config.config_path()  # also indirectly calls data_dir()
    config.db_path()

    # Exactly one mkdir for our fresh path; any incidental calls would be
    # for other paths (none expected here).
    fresh_resolved = fresh.expanduser()
    assert sum(1 for p in calls if p == fresh_resolved) == 1, calls


def test_data_dir_raises_wisp_config_error_on_mkdir_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A permission error or unwritable parent must surface as
    WispConfigError, not a raw OSError."""
    monkeypatch.setenv("WISP_DATA_DIR", str(tmp_path / "denied"))

    def boom(self: Path, *args: object, **kwargs: object) -> None:
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(Path, "mkdir", boom)

    with pytest.raises(WispConfigError, match="Cannot create Wisp data directory"):
        config.data_dir()


def test_save_fsyncs_data_before_rename(monkeypatch: pytest.MonkeyPatch) -> None:
    """save() must flush + fsync the tmp file before atomic rename, so a
    power loss between rename-returns and disk-write doesn't lose data.

    Addresses PR#17 review comment: "What happen when config change
    on-the-fly and the app just die?"
    """
    fsync_calls: list[int] = []
    real_fsync = os.fsync

    def tracking_fsync(fd: int) -> None:
        fsync_calls.append(fd)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", tracking_fsync)

    config.save(Config(profile=Profile(target_role="x")))
    assert len(fsync_calls) == 1, "save() should fsync exactly once before rename"


def test_load_raises_on_corrupt_json() -> None:
    """A garbled config file must surface as WispConfigError with line info,
    not a raw JSONDecodeError."""
    config.config_path().write_text("{not valid json,,,}", encoding="utf-8")
    with pytest.raises(WispConfigError, match="not valid JSON"):
        config.load()


def test_load_raises_on_schema_violation() -> None:
    """JSON with the wrong types for known fields must surface as
    WispConfigError, not pydantic's ValidationError."""
    config.config_path().write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile": {"salary_floor": "not-a-number-and-not-coercible"},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(WispConfigError, match="invalid structure"):
        config.load()


def test_is_first_run_does_not_lie_when_config_is_corrupt() -> None:
    """is_first_run() must NOT return True for a corrupt-but-present config.
    Treating a loader error as 'first run' would silently overwrite the
    user's broken-but-recoverable config when the wizard re-saves.

    Addresses PR#17 review comment: "Could be the config loader error,
    not first run."
    """
    config.config_path().write_text("{garbage", encoding="utf-8")
    with pytest.raises(WispConfigError):
        config.is_first_run()


def test_save_failure_cleans_partial_tmp(monkeypatch: pytest.MonkeyPatch) -> None:
    """If json.dump or fsync fails, the partial .tmp must not be left behind
    to confuse the next load."""

    def boom(_fd: int) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(os, "fsync", boom)

    with pytest.raises(WispConfigError, match="Cannot write"):
        config.save(Config(profile=Profile(target_role="x")))

    tmp = config.config_path().with_suffix(".json.tmp")
    assert not tmp.exists(), "partial tmp file should be cleaned on failure"
