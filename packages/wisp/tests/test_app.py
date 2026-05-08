"""Tests for the Flask app surface — first-run gate, route placeholders,
template rendering, static assets.

The autouse ``isolated_wisp_data_dir`` fixture (in ``conftest.py``)
points every test at a temp ``WISP_DATA_DIR``, so by default each test
starts with no config — i.e. the first-run gate is active. Tests that
need a completed-setup state save a Profile before issuing requests.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from flask.testing import FlaskClient

from wisp import __version__
from wisp.app import create_app
from wisp.config import Config, Profile, save


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    """Test client with NO profile set — first-run gate is active."""
    yield create_app().test_client()


@pytest.fixture
def post_setup_client() -> Iterator[FlaskClient]:
    """Test client with a profile already saved — gate is satisfied."""
    save(Config(profile=Profile(target_role="Senior Product Designer")))
    yield create_app().test_client()


# ---- First-run gate -------------------------------------------------------


def test_root_redirects_to_setup_on_first_run(client: FlaskClient) -> None:
    """The whole point of the gate: a user with no profile lands on /setup."""
    resp = client.get("/")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/setup/")


def test_setup_itself_is_not_gated(client: FlaskClient) -> None:
    """If /setup were gated, we'd loop. The exempt prefix prevents that."""
    resp = client.get("/setup/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Welcome to Wisp" in body


def test_healthz_is_not_gated(client: FlaskClient) -> None:
    """Operational endpoint must respond regardless of config state."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok", "version": __version__}


def test_static_assets_are_not_gated(client: FlaskClient) -> None:
    """The wizard depends on /static/wisp.css; gating it would break the
    first-run page."""
    resp = client.get("/static/wisp.css")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    # Sanity: this is the design-token CSS, not a 404 / placeholder
    assert "--ink:" in body
    assert "wisp-shell" in body


def test_gate_lets_traffic_through_after_setup(
    post_setup_client: FlaskClient,
) -> None:
    """Once a profile is saved, the gate stops redirecting."""
    resp = post_setup_client.get("/")
    assert resp.status_code == 200


# ---- Route placeholders --------------------------------------------------


@pytest.mark.parametrize(
    ("path", "expected_marker"),
    [
        ("/", "Your jobs"),
        ("/jobs", "Your jobs"),
        ("/jobs/new", "Add a job"),
        ("/jobs/42", "Job detail"),
        ("/overview", "Overview"),
        ("/settings", "Settings"),
    ],
)
def test_route_placeholder_renders(
    post_setup_client: FlaskClient, path: str, expected_marker: str
) -> None:
    """Every M6.4 placeholder route returns 200 with its expected
    headline. Catches a missing template / typo'd url_for early."""
    resp = post_setup_client.get(path)
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"
    body = resp.get_data(as_text=True)
    assert expected_marker in body, f"{path} missing {expected_marker!r}"


def test_detail_route_passes_job_id_to_template(
    post_setup_client: FlaskClient,
) -> None:
    resp = post_setup_client.get("/jobs/123")
    body = resp.get_data(as_text=True)
    assert "Job #123" in body


# ---- Template chrome ----------------------------------------------------


def test_base_template_includes_version_in_rail_footer(
    post_setup_client: FlaskClient,
) -> None:
    """Every page renders ``v<version>`` in the rail footer via the
    context_processor injected in create_app()."""
    resp = post_setup_client.get("/")
    body = resp.get_data(as_text=True)
    assert f"v{__version__}" in body


def test_base_template_pulls_in_design_tokens(
    post_setup_client: FlaskClient,
) -> None:
    """The base template links the wisp.css static asset; verify the
    href is correct (a typo'd url_for would show as a literal '/static
    /wrong.css' in the body)."""
    resp = post_setup_client.get("/")
    body = resp.get_data(as_text=True)
    assert 'href="/static/wisp.css"' in body


def test_base_template_loads_bootstrap_via_cdn(
    post_setup_client: FlaskClient,
) -> None:
    """Stack decision (per plan): Bootstrap 5 from CDN. Pinned via SRI."""
    resp = post_setup_client.get("/")
    body = resp.get_data(as_text=True)
    assert "bootstrap@5.3.3" in body
    assert "integrity=" in body  # SRI hash present


# ---- Active-nav highlighting --------------------------------------------


@pytest.mark.parametrize(
    ("path", "active_label"),
    [
        ("/", "Jobs"),
        ("/jobs", "Jobs"),
        ("/overview", "Overview"),
        ("/settings", "Settings"),
    ],
)
def test_nav_marks_current_view_active(
    post_setup_client: FlaskClient, path: str, active_label: str
) -> None:
    """The rail's `current_view` highlights the active page so users
    know where they are without reading."""
    resp = post_setup_client.get(path)
    body = resp.get_data(as_text=True)
    # The active class only attaches to the matching nav button.
    # Every page has all three labels in the nav; only one is `active`.
    assert "wisp-rail-btn active" in body
    # Crude but effective: the active class appears in close proximity to
    # the active label
    active_index = body.find("wisp-rail-btn active")
    label_index = body.find(active_label, active_index)
    assert label_index != -1, f"active class not near {active_label!r}"
    assert label_index - active_index < 400  # within the same anchor block
