"""Offline tests: none of these need a database."""

import re

import pytest

from app import create_app
from app import validators
from app.auth_utils import hash_password, verify_password
from app.models import matching_model as mm
from app.services import requirement_service as rs


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_password_hash_roundtrip():
    h = hash_password("TestPassword123")
    assert verify_password("TestPassword123", h)
    assert not verify_password("wrong", h)


def test_validators():
    assert validators.is_valid_email("a@b.co")
    assert not validators.is_valid_email("nope")
    assert validators.is_valid_phone("98765 43210")
    assert not validators.is_valid_phone("123")
    assert validators.is_valid_pincode("560001")
    assert not validators.is_valid_pincode("5600")
    assert validators.parse_experience_years("3") == (3, None)
    assert validators.parse_experience_years(True)[0] is None
    assert validators.parse_experience_years(-1)[0] is None
    assert validators.clean_text(None) == ""


def test_matching_helpers():
    assert mm._weekday_number("monday") == 1
    assert mm._time_to_seconds("09:30") == 9 * 3600 + 1800
    assert mm._experience_requirement_years("3") == 3.0
    assert mm._experience_requirement_years(None) is None


def test_salary_estimate(monkeypatch):
    monkeypatch.setattr(rs, "get_service_pricing", lambda ids: [
        {"service_id": 1, "service_name": "Cooking",
         "base_monthly_rate": 6000, "rate_per_extra_hour": 100},
    ])
    ok, result = rs.estimate_monthly_salary(
        [1],
        [{"day_of_week": "MONDAY", "start_time": "09:00", "end_time": "11:00"}],
    )
    assert ok
    # 1 working day: 6000*1/6 + 1 extra hour * 100 * 52/12
    assert result["estimated_monthly_salary"] == pytest.approx(1433.33, abs=0.01)


def test_requirement_validation_rejects_bad_input():
    ok, msg = rs.create_household_requirement(
        1, None, 5, [], "12", "x", None, [1], [])
    assert not ok


def test_register_validation_without_db():
    from app.services.auth_service import register_user
    ok, msg = register_user("A", "bad-email", "9876543210", "password1", "MAID")
    assert not ok and "email" in msg.lower()
    ok, msg = register_user("A", "a@b.co", "9876543210", "short", "MAID")
    assert not ok and "8" in msg
    ok, msg = register_user("A", "a@b.co", "9876543210", "password1", "ADMIN")
    assert not ok


def test_register_endpoint_rejects_non_json(client):
    assert client.post("/auth/register", data="x").status_code == 400
    assert client.post("/auth/login", json=[1]).status_code == 400


def test_protected_pages_redirect_browsers_and_json_for_api(client):
    page = client.get("/customer/dashboard", headers={"Accept": "text/html"})
    assert page.status_code == 302 and page.headers["Location"].endswith("/login")
    api = client.get("/customer/assignments")
    assert api.status_code == 401 and api.get_json()["success"] is False


def test_root_redirects_and_debug_endpoints_hidden(client):
    assert client.get("/").status_code == 302
    assert client.get("/session-test").status_code == 404
    assert client.get("/db-test").status_code == 404


def test_all_frontend_urls_match_a_route():
    """Every URL written in a template or JS file must hit a real route."""
    import os
    app = create_app()
    rules = [re.compile("^" + re.sub(r"<[^>]+>", "[^/]+", r.rule) + "$")
             for r in app.url_map.iter_rules()]
    base = os.path.join(os.path.dirname(__file__), "..", "app")
    url_re = re.compile(
        r"""["'`](/(?:[\w\-.]+|\$\{[^}]*\}|\{\{[^}]*\}\})"""
        r"""(?:/(?:[\w\-.]*|\$\{[^}]*\}|\{\{[^}]*\}\}))*/?)["'`]""")
    missing = []
    for folder, _, files in os.walk(base):
        for name in files:
            if not name.endswith((".html", ".js")):
                continue
            text = open(os.path.join(folder, name), encoding="utf-8").read()
            for m in url_re.finditer(text):
                url = re.sub(r"\$\{[^}]*\}|\{\{[^}]*\}\}", "1", m.group(1))
                if url.startswith("/static/"):
                    continue
                if not any(r.match(url) for r in rules):
                    missing.append((name, m.group(1)))
    assert not missing, missing
