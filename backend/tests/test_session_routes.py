"""QA-Gate: /sessions HTTP router — auth, CRUD, owner-scoped 404s."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.api.deps import get_current_user
from app.core import auth, session_service
from app.core.db import get_session
from app.main import app
from app.models.entities import User

_eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(_eng)

with Session(_eng) as _s:
    _u1 = auth.signup(_s, organization_name="A", email="s1@x.de", password="pw123456", display_name="S1")
    _u2 = auth.signup(_s, organization_name="B", email="s2@x.de", password="pw123456", display_name="S2")
    _U1, _U2 = _u1.id, _u2.id
    # a session owned by u2, used to prove u1 cannot touch it
    _foreign = session_service.create_session(_s, user=_s.get(User, _U2)).id


def _sess_override():
    with Session(_eng) as s:
        yield s


def _as_u1() -> User:
    with Session(_eng) as s:
        return s.get(User, _U1)


@pytest.fixture(autouse=True)
def _overrides():
    app.dependency_overrides[get_session] = _sess_override
    yield
    app.dependency_overrides.pop(get_session, None)
    app.dependency_overrides.pop(get_current_user, None)


client = TestClient(app)


def test_sessions_require_auth():
    assert client.get("/sessions").status_code == 401
    assert client.post("/sessions", json={}).status_code == 401


def test_session_crud_roundtrip():
    app.dependency_overrides[get_current_user] = _as_u1
    created = client.post("/sessions", json={})
    assert created.status_code == 201
    sid = created.json()["id"]
    # appears in the list
    assert any(s["id"] == sid for s in client.get("/sessions").json())
    # messages empty initially
    assert client.get(f"/sessions/{sid}/messages").json() == []
    # rename
    r = client.patch(f"/sessions/{sid}", json={"title": "Mein Titel"})
    assert r.status_code == 200 and r.json()["title"] == "Mein Titel"
    # delete
    assert client.delete(f"/sessions/{sid}").status_code == 204
    assert client.delete(f"/sessions/{sid}").status_code == 404  # gone


def test_cannot_touch_foreign_session():
    app.dependency_overrides[get_current_user] = _as_u1
    assert client.get(f"/sessions/{_foreign}/messages").status_code == 404
    assert client.patch(f"/sessions/{_foreign}", json={"title": "hack"}).status_code == 404
    assert client.delete(f"/sessions/{_foreign}").status_code == 404
