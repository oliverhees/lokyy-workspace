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


def _sess():
    with Session(_eng) as s:
        yield s


def _cu() -> User:
    with Session(_eng) as s:
        return s.get(User, _UID)


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
