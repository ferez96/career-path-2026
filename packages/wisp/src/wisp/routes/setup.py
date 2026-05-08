"""First-run setup wizard.

M6 ships a placeholder ``/setup`` so the first-run-gate middleware has
a target. M7 fills in the multi-step profile form + AI provider
auto-detect.
"""

from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("setup", __name__, url_prefix="/setup")


@bp.get("/")
def show() -> str:
    """The wizard. M7.1 turns this into a real form."""
    return render_template("setup.html", current_view="setup")
