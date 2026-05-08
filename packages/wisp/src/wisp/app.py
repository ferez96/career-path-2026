"""Flask application factory.

Constructs the Wisp web app. Templates live at ``packages/wisp/src/wisp/templates``
and static assets at ``packages/wisp/src/wisp/static``; both are bundled into
the wheel via Hatchling's package include.

Two blueprints are registered:

  * ``main`` — the primary app surface (``/``, ``/jobs/*``, ``/overview``,
    ``/settings``, ``/healthz``)
  * ``setup`` — the first-run wizard at ``/setup``

The first-run-gate middleware (in :mod:`wisp.middleware`) redirects every
non-exempt request to ``/setup`` until the user has completed the wizard.
"""

from __future__ import annotations

from flask import Flask

from . import __version__
from .middleware import register_middleware
from .routes.main import bp as main_bp
from .routes.setup import bp as setup_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # Make the package version available to every template (footer copy).
    @app.context_processor
    def _inject_globals() -> dict[str, object]:
        return {"wisp_version": __version__}

    register_middleware(app)
    app.register_blueprint(main_bp)
    app.register_blueprint(setup_bp)
    return app
