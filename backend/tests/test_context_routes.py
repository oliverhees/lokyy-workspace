"""M2.1: /context HTTP route — auth + soul/profile round-trip."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.api.deps import get_current_user
from app.core import auth, context_service
from app.core.db import get_session
from app.main import app
from app.models.entities import User

_eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(_eng)

with Session(_eng) as _s:
    _u = auth.signup(_s, organization_name="A", email="ctx@x.de", password="pw123456", display_name="C")
    _UID = _u.id

with Session(_eng) as _s:
    _u_b = auth.signup(_s, organization_name="B", email="ctx-b@x.de", password="pw123456", display_name="D")
    _UID_B = _u_b.id


def _sess():
    with Session(_eng) as s:
        yield s


def _cu() -> User:
    with Session(_eng) as s:
        return s.get(User, _UID)


def _cu_b() -> User:
    with Session(_eng) as s:
        return s.get(User, _UID_B)


@pytest.fixture(autouse=True)
def _ov():
    app.dependency_overrides[get_session] = _sess
    yield
    app.dependency_overrides.pop(get_session, None)
    app.dependency_overrides.pop(get_current_user, None)


client = TestClient(app)


def test_context_requires_auth():
    assert client.get("/context").status_code == 401


def test_context_roundtrip():
    app.dependency_overrides[get_current_user] = _cu
    # default soul present on first read
    got = client.get("/context")
    assert got.status_code == 200
    assert got.json()["soul"] == context_service.DEFAULT_SOUL
    # update + persist
    put = client.put("/context", json={"soul": "Antworte auf Bairisch.", "user_profile": "Mag Kaffee."})
    assert put.status_code == 200 and put.json()["soul"] == "Antworte auf Bairisch."
    assert client.get("/context").json()["user_profile"] == "Mag Kaffee."


def test_context_is_tenant_isolated():
    """Cross-Tenant (M2 QA, LWS-65): user B never reads user A's context via the route.

    The route derives the workspace from get_current_user (_workspace_id); this pins
    that derivation so a refactor can't silently serve another tenant's context.
    """
    # User A writes distinctive context.
    app.dependency_overrides[get_current_user] = _cu
    put = client.put("/context", json={"soul": "Geheim-Soul von A.", "user_profile": "Projekt Zeta."})
    assert put.status_code == 200
    # User B reads — gets their own fresh context, never A's.
    app.dependency_overrides[get_current_user] = _cu_b
    got = client.get("/context")
    assert got.status_code == 200
    body = got.json()
    assert body["soul"] == context_service.DEFAULT_SOUL
    assert "Geheim-Soul" not in body["soul"]
    assert "Zeta" not in body["user_profile"]
