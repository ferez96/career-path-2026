"""Local-server launcher.

Picks a free port (when requested), schedules a browser tab to open once the
server is ready, and runs Flask in the foreground. The user quits with Ctrl-C;
closing the browser tab leaves the server running so they can reopen it.

This module is deliberately small. M6 replaces the placeholder app factory; the
launcher itself should not need to change.
"""

from __future__ import annotations

import socket
import threading
import webbrowser
from dataclasses import dataclass

from .app import create_app


@dataclass(frozen=True)
class LaunchOptions:
    host: str = "127.0.0.1"
    port: int = 0  # 0 means "pick a free port"
    open_browser: bool = True
    browser_delay_seconds: float = 0.6


def pick_free_port(host: str = "127.0.0.1") -> int:
    """Ask the OS for a free TCP port on ``host``."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


def _schedule_browser_open(url: str, delay_seconds: float) -> threading.Timer:
    """Open the browser after a short delay so the server is ready.

    The Timer thread is daemonized so an early ``Ctrl-C`` (before the delay
    elapses) lets the process exit cleanly instead of blocking on the pending
    ``webbrowser.open`` call. Returns the timer for tests / cleanup.
    """
    timer = threading.Timer(delay_seconds, lambda: webbrowser.open(url))
    timer.daemon = True
    timer.start()
    return timer


def serve(options: LaunchOptions | None = None) -> None:
    """Start the Wisp web app. Blocks until the user terminates the process."""
    options = options or LaunchOptions()
    port = options.port or pick_free_port(options.host)
    url = f"http://{options.host}:{port}/"

    print(f"Wisp running at {url}  (Ctrl-C to stop)")

    if options.open_browser:
        _schedule_browser_open(url, options.browser_delay_seconds)

    app = create_app()
    # use_reloader=False: launching twice from a single command would cause
    # two browser tabs and confuse the port pick. Production-quality WSGI
    # servers come later; the dev server is fine for a local desktop tool.
    app.run(host=options.host, port=port, threaded=True, use_reloader=False)
