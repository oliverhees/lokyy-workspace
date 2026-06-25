"""Auth HTTP endpoints: signup/login/me, admin-only register, logout revoke, API token."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.core.db import get_session
from app.main import app

_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SQLModel.metadata.create_all(_engine)


def _override():
    with Session(_engine) as s:
        yield s


@pytest.fixture(autouse=True)
def _override_session():
    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.pop(get_session, None)


def _signup(client: TestClient, email: str, org: str = "Acme") -> object:
    return client.post("/auth/signup", json={
        "organization_name": org, "email": email,
        "password": "pw12345678", "display_name": "U",
    })


def test_signup_login_me_and_unauth():
    client = TestClient(app)
    r = _signup(client, "a@example.de")
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "a@example.de" and r.json()["is_org_admin"] is True
    # signup auto-logs in
    assert client.get("/auth/me").json()["email"] == "a@example.de"
    # a fresh (cookie-less) client is rejected
    assert TestClient(app).get("/auth/me").status_code == 401


def test_login_wrong_password_rejected():
    client = TestClient(app)
    _signup(client, "b@example.de")
    assert client.post("/auth/login", json={"email": "b@example.de", "password": "nope"}).status_code == 401


def test_signup_duplicate_email_conflict():
    _signup(TestClient(app), "dup@example.de")
    assert _signup(TestClient(app), "dup@example.de").status_code == 409


def test_register_requires_admin_auth():
    # unauthenticated register is rejected
    assert TestClient(app).post("/auth/register", json={
        "email": "x@example.de", "password": "pw12345678", "display_name": "X",
    }).status_code == 401
    # an org admin can add a member to their own org (org derived from session)
    admin = TestClient(app)
    _signup(admin, "admin@example.de", org="Beta")
    r = admin.post("/auth/register", json={
        "email": "member@example.de", "password": "pw12345678", "display_name": "M",
    })
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "member@example.de"


def test_logout_revokes_session():
    client = TestClient(app)
    _signup(client, "lo@example.de")
    assert client.get("/auth/me").status_code == 200
    assert client.post("/auth/logout").status_code == 204
    # session is revoked server-side, not just cookie-cleared
    assert client.get("/auth/me").status_code == 401


def test_api_token_auth_works():
    client = TestClient(app)
    _signup(client, "c@example.de")  # auto-login
    raw = client.post("/auth/tokens", json={"name": "CI", "scopes": "chat"}).json()["token"]
    r = TestClient(app).get("/auth/me", headers={"Authorization": f"Bearer {raw}"})
    assert r.status_code == 200 and r.json()["email"] == "c@example.de"


def test_2fa_login_gate():
    """A 2FA-enabled user must provide a valid TOTP code at login."""
    import pyotp

    client = TestClient(app)
    _signup(client, "tfa@example.de")  # auto-logged in
    secret = client.post("/auth/2fa/setup").json()["secret"]
    codes = client.post("/auth/2fa/enable", json={"code": pyotp.TOTP(secret).now()}).json()
    assert "backup_codes" in codes
    # fresh client: login without code → 401
    fresh = TestClient(app)
    assert fresh.post("/auth/login", json={"email": "tfa@example.de", "password": "pw12345678"}).status_code == 401
    # with a valid code → 200
    ok = fresh.post("/auth/login", json={
        "email": "tfa@example.de", "password": "pw12345678", "totp_code": pyotp.TOTP(secret).now(),
    })
    assert ok.status_code == 200
