"""T0.4: auth HTTP endpoints — register → login → me, and unauth rejection."""
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.core.db import get_session
from app.main import app
from app.models.entities import Organization

# Shared in-memory DB across requests (StaticPool keeps one connection).
_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SQLModel.metadata.create_all(_engine)


def _override():
    with Session(_engine) as s:
        yield s


app.dependency_overrides[get_session] = _override


def _make_org() -> str:
    with Session(_engine) as s:
        o = Organization(name="Acme")
        s.add(o)
        s.commit()
        s.refresh(o)
        return o.id


def test_register_login_me_and_unauth():
    org_id = _make_org()
    client = TestClient(app)

    r = client.post("/auth/register", json={
        "organization_id": org_id, "email": "a@example.de",
        "password": "pw12345678", "display_name": "A",
    })
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "a@example.de"

    # unauthenticated /me is rejected
    assert TestClient(app).get("/auth/me").status_code == 401

    # login sets the session cookie; /me then works on the same client
    r = client.post("/auth/login", json={"email": "a@example.de", "password": "pw12345678"})
    assert r.status_code == 200, r.text
    r = client.get("/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "a@example.de"


def test_login_wrong_password_rejected():
    org_id = _make_org()
    client = TestClient(app)
    client.post("/auth/register", json={
        "organization_id": org_id, "email": "b@example.de",
        "password": "pw12345678", "display_name": "B",
    })
    r = client.post("/auth/login", json={"email": "b@example.de", "password": "nope"})
    assert r.status_code == 401


def test_api_token_auth_works():
    org_id = _make_org()
    client = TestClient(app)
    client.post("/auth/register", json={
        "organization_id": org_id, "email": "c@example.de",
        "password": "pw12345678", "display_name": "C",
    })
    client.post("/auth/login", json={"email": "c@example.de", "password": "pw12345678"})
    raw = client.post("/auth/tokens", json={"name": "CI", "scopes": "chat"}).json()["token"]
    # fresh client, no cookie — authenticate via Bearer token
    r = TestClient(app).get("/auth/me", headers={"Authorization": f"Bearer {raw}"})
    assert r.status_code == 200
    assert r.json()["email"] == "c@example.de"
