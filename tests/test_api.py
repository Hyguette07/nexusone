"""API smoke tests — SQLite + in-memory pub/sub, no Redis required."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "data").mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="module")
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "simulation" in body["disclaimer"].lower()
    assert body["pubsub_mode"] in {"memory", "redis"}


def test_login_seed_dispatcher_and_dashboard(client: TestClient):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "dispatcher@nexusone.local", "password": "ChangeMe123!"},
    )
    assert res.status_code == 200
    token = res.json()["data"]["token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["role"] == "DISPATCHER"

    dash = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash.status_code == 200
    data = dash.json()["data"]
    assert data["open_count"] >= 1
    assert "recent_incidents" in data


def test_citizen_reports_incident(client: TestClient):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "citizen@nexusone.local", "password": "ChangeMe123!"},
    )
    token = login.json()["data"]["token"]
    res = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test flood at Nyabugogo",
            "description": "Simulation report created by pytest.",
            "incident_type": "FLOOD",
            "severity": "MEDIUM",
            "latitude": -1.94,
            "longitude": 30.05,
            "location_name": "Nyabugogo",
        },
    )
    assert res.status_code == 201
    assert res.json()["data"]["status"] == "OPEN"


def test_rankings_for_seed_fire(client: TestClient):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "dispatcher@nexusone.local", "password": "ChangeMe123!"},
    )
    token = login.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    incidents = client.get("/api/v1/incidents", headers=headers).json()["data"]
    fire = next(i for i in incidents if i["incident_type"] == "FIRE")
    ranked = client.get(f"/api/v1/incidents/{fire['id']}/rankings", headers=headers)
    assert ranked.status_code == 200
    top = ranked.json()["data"][0]
    assert top["resource_type"] == "FIRE_UNIT"
    assert top["score"] > 0
