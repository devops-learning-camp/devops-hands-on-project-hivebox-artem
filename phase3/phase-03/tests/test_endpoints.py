"""
Unit tests for Phase-03 API endpoints.

We mock out SenseMapClient.fetch_temperatures(...) so tests do NOT rely on the
external openSenseMap API. This keeps CI stable and fast.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.service import SenseMapClient

client = TestClient(app)


# --------------------------
# /version
# --------------------------

def test_version_endpoint_ok():
    r = client.get("/version")
    assert r.status_code == 200
    js = r.json()
    assert "version" in js
    assert isinstance(js["version"], str)
    assert js["version"].startswith("v")


def test_version_respects_env(monkeypatch):
    from app import settings as app_settings
    from app import main as app_main

    monkeypatch.setenv("APP_VERSION", "v9.9.9")
    app_settings.APP_VERSION = "v9.9.9"
    app_main.APP_VERSION = "v9.9.9"

    r = client.get("/version")
    assert r.status_code == 200
    assert r.json()["version"] == "v9.9.9"


# --------------------------
# /temperature
# --------------------------

def test_temperature_average_ok(monkeypatch):
    async def fake_fetch(self, hours=None):
        # Three recent measurements: avg = 22.0
        return [20.0, 22.0, 24.0]

    monkeypatch.setattr(SenseMapClient, "fetch_temperatures", fake_fetch)
    r = client.get("/temperature")
    assert r.status_code == 200
    js = r.json()
    assert "average_temperature" in js
    assert js["average_temperature"] == 22.0
    assert js.get("unit") == "°C"


def test_temperature_rounding(monkeypatch):
    async def fake_fetch(self, hours=None):
        # Avg = (20.111 + 20.115) / 2 = 20.113 -> round(..., 2) = 20.11
        return [20.111, 20.115]

    monkeypatch.setattr(SenseMapClient, "fetch_temperatures", fake_fetch)
    r = client.get("/temperature")
    assert r.status_code == 200
    js = r.json()
    assert js["average_temperature"] == 20.11


def test_temperature_no_data(monkeypatch):
    async def fake_fetch(self, hours=None):
        # No measurements within the lookback window
        return []

    monkeypatch.setattr(SenseMapClient, "fetch_temperatures", fake_fetch)
    r = client.get("/temperature")
    assert r.status_code == 404
    assert "No temperature data" in r.json()["detail"]
