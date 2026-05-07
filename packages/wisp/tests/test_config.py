"""Tests for ``wisp.config`` — round-trip, first-run, schema drift, normalization."""

from __future__ import annotations

import json
from pathlib import Path

from wisp import config
from wisp.config import AIKeys, Config, Profile


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
