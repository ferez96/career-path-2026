"""Tests for ``wisp.app`` and ``wisp.launcher``."""

from __future__ import annotations

import socket

from wisp import __version__
from wisp.app import create_app
from wisp.launcher import _schedule_browser_open, pick_free_port


def test_pick_free_port_returns_bindable_port() -> None:
    port = pick_free_port()
    assert isinstance(port, int)
    assert 1024 < port < 65536
    # Must actually be free at the moment of call
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", port))


def test_index_page_renders_version() -> None:
    client = create_app().test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Wisp" in body
    assert __version__ in body


def test_healthz_returns_ok_and_version() -> None:
    client = create_app().test_client()
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok", "version": __version__}


def test_browser_timer_is_daemonized() -> None:
    """An early Ctrl-C must not block on a pending webbrowser.open."""
    timer = _schedule_browser_open("http://127.0.0.1:1/", delay_seconds=10.0)
    try:
        assert timer.daemon is True
    finally:
        timer.cancel()
