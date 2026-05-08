"""Tests for ``wisp.launcher`` (port-pick + browser Timer).

The Flask app surface itself lives in ``test_app.py`` — this file
focuses on the launcher-specific concerns from M1.3.
"""

from __future__ import annotations

import socket

from wisp.launcher import _schedule_browser_open, pick_free_port


def test_pick_free_port_returns_bindable_port() -> None:
    port = pick_free_port()
    assert isinstance(port, int)
    assert 1024 < port < 65536
    # Must actually be free at the moment of call
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", port))


def test_browser_timer_is_daemonized() -> None:
    """An early Ctrl-C must not block on a pending webbrowser.open."""
    timer = _schedule_browser_open("http://127.0.0.1:1/", delay_seconds=10.0)
    try:
        assert timer.daemon is True
    finally:
        timer.cancel()
