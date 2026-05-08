"""Primary app routes.

Each handler is a thin shell in M6 — the real logic lands milestone-by-
milestone (list view in M9, add-job in M8, decision actions in M10,
overview in M12, settings in M13). The placeholder pages exist so the
nav shell is navigable end-to-end while later milestones fill in the
content.
"""

from __future__ import annotations

from flask import Blueprint, render_template

from .. import __version__

bp = Blueprint("main", __name__)


@bp.get("/")
def index() -> str:
    """Job list. Will be the hot list-view in M9."""
    return render_template("list.html", current_view="jobs")


@bp.get("/jobs")
def jobs_list() -> str:
    """Filtered list view. Same template as ``/`` for now; M9 wires
    the ``filter`` query param into the adapter call."""
    return render_template("list.html", current_view="jobs")


@bp.get("/jobs/new")
def jobs_new() -> str:
    """Manual paste-JD form. M8.1 fills in the form fields."""
    return render_template("add_job.html", current_view="jobs")


@bp.get("/jobs/<int:job_id>")
def jobs_detail(job_id: int) -> str:
    """Detail view with the hot brief. M9.2 fills in the brief +
    cold-storage collapse."""
    return render_template("detail.html", current_view="jobs", job_id=job_id)


@bp.get("/overview")
def overview() -> str:
    """KPIs + calibration table. M12 wires the data."""
    return render_template("overview.html", current_view="overview")


@bp.get("/settings")
def settings() -> str:
    """Profile + AI provider config. M13 wires the form."""
    return render_template("settings.html", current_view="settings")


@bp.get("/healthz")
def healthz() -> dict[str, str]:
    """Operational health check; never gated by first-run middleware."""
    return {"status": "ok", "version": __version__}
