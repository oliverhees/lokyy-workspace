"""Smoke tests for the M0/T0.2 foundation: the app boots and /health responds."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "env" in body
    assert "version" in body


def test_root_ok():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Lokyy Workspace API"
