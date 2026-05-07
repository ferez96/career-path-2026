"""Shared pytest fixtures.

The default fixture isolates every test under a temporary ``WISP_DATA_DIR``
so they neither read from nor write to the user's real Wisp config.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_wisp_data_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Path]:
    monkeypatch.setenv("WISP_DATA_DIR", str(tmp_path))
    yield tmp_path
