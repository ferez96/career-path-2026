"""First-run gate.

Until the setup wizard has been completed, every non-exempt request is
redirected to ``/setup``. Exempt prefixes:

  * ``/setup`` — the wizard itself, otherwise we'd loop
  * ``/static`` — Flask serves static assets here; the wizard needs CSS
  * ``/healthz`` — operational endpoint, must not require config

A corrupt config file (per :class:`WispConfigError`) is *not* caught
here — it propagates so the user sees a real error rather than being
silently bounced into the wizard, which would overwrite their broken-
but-recoverable config on save.
"""

from __future__ import annotations

from collections.abc import Iterable

from flask import Flask, redirect, request, url_for
from werkzeug.wrappers import Response

from .config import is_first_run

_EXEMPT_PREFIXES: tuple[str, ...] = ("/setup", "/static", "/healthz")


def register_middleware(app: Flask, exempt_prefixes: Iterable[str] | None = None) -> None:
    """Wire the first-run gate onto ``app``.

    ``exempt_prefixes`` overrides the default list — useful for tests
    that need to exempt extra paths.
    """
    prefixes = tuple(exempt_prefixes) if exempt_prefixes is not None else _EXEMPT_PREFIXES

    @app.before_request
    def _first_run_gate() -> Response | None:
        if request.path.startswith(prefixes):
            return None
        if is_first_run():
            return redirect(url_for("setup.show"))
        return None
