"""F3: /settings routes — auth enforcement + authed round-trip (SQLite override)."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (register all tables)
from app.api.deps import get_current_user
from app.core import auth
from app.core.db import get_session
from app.main import app
from app.models.entities import User

# Shared in-memory DB across connections (StaticPool) so the seeded user and the
# request-time sessions see the same data.
_eng = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SQLModel.metadata.create_all(_eng)

with Session(_eng) as _s:
    _user = auth.signup(_s, organization_name="Acme", email="r@x.de",
                        password="pw123456", display_name="Routey")
    _USER_ID = _user.id


def _session_override():
    with Session(_eng) as s:
        yield s


def _current_user_override() -> User:
    with Session(_eng) as s:
        return s.get(User, _USER_ID)


client = TestClient(app)


@pytest.fixture(autouse=True)
def _override_session():
    app.dependency_overrides[get_session] = _session_override
    yield
    app.dependency_overrides.pop(get_session, None)


def test_settings_requires_auth():
    # No authenticated user (no override) → the real dependency returns 401.
    resp = client.get("/settings")
    assert resp.status_code == 401


def test_settings_roundtrip_when_authed():
    app.dependency_overrides[get_current_user] = _current_user_override
    try:
        # defaults on first read
        got = client.get("/settings")
        assert got.status_code == 200
        data = got.json()
        assert data["language"] == "de" and data["theme"] == "dark"
        assert data["email"] == "r@x.de" and data["display_name"] == "Routey"

        # update + persistence
        put = client.put("/settings", json={"language": "en", "theme": "light"})
        assert put.status_code == 200
        assert put.json()["language"] == "en" and put.json()["theme"] == "light"
        assert client.get("/settings").json()["language"] == "en"

        # invalid value rejected by the Literal schema (422)
        bad = client.put("/settings", json={"language": "fr"})
        assert bad.status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_user, None)
