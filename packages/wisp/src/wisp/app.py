"""Flask application factory.

This is the M1.3 placeholder. The real routes/templates land in M6+.
For now, ``/`` returns a small "Hello Wisp" page so the launcher and the
end-to-end install can be exercised before storage and UI exist.
"""

from __future__ import annotations

from flask import Flask

from . import __version__


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return (
            "<!doctype html>"
            "<html lang='en'><head><meta charset='utf-8'>"
            "<title>Wisp</title>"
            "<style>body{font-family:system-ui,sans-serif;max-width:560px;"
            "margin:8rem auto;padding:0 1rem;color:#1c1917;background:#f8f7f4}"
            "h1{font-weight:400;letter-spacing:-0.01em}"
            "code{background:#f1efe9;padding:2px 6px;border-radius:4px}</style>"
            "</head><body>"
            "<h1>Wisp</h1>"
            f"<p>Version <code>{__version__}</code> &mdash; foundation skeleton (M1).</p>"
            "<p>Setup wizard, jobs, evaluations, and the rest of the UI "
            "land in milestones M6 onward.</p>"
            "</body></html>"
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    return app
