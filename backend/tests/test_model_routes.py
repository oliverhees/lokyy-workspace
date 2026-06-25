"""F4: /models routes — auth, CRUD round-trip, and key never returned in plaintext."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.deps import get_current_user
from app.core import auth
from app.core.db import get_session
from app.main import app
from app.models.entities import User

_eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(_eng)

with Session(_eng) as _s:
    _user = auth.signup(_s, organization_name="Acme", email="m@x.de",
                        password="pw123456", display_name="Modely")
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


def test_models_requires_auth():
    assert client.get("/models").status_code == 401


def test_discover_requires_auth():
    assert client.post("/models/discover", json={"provider": "openrouter"}).status_code == 401


def test_discover_without_base_url_is_rejected():
    app.dependency_overrides[get_current_user] = _current_user_override
    try:
        # native providers (no base_url) → manual entry, friendly 400
        r = client.post("/models/discover", json={"provider": "anthropic", "base_url": ""})
        assert r.status_code == 400
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_discover_connection_error_is_friendly_400():
    app.dependency_overrides[get_current_user] = _current_user_override
    try:
        # loopback is allowed (local models) but nothing listens → friendly 400, not 500
        r = client.post("/models/discover", json={
            "provider": "custom", "base_url": "http://127.0.0.1:1/v1", "api_key": "",
        })
        assert r.status_code == 400
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_discover_blocks_internal_metadata_url():
    app.dependency_overrides[get_current_user] = _current_user_override
    try:
        r = client.post("/models/discover", json={
            "provider": "custom", "base_url": "http://169.254.169.254/latest", "api_key": "",
        })
        assert r.status_code == 400  # SSRF guard
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_models_crud_and_key_never_returned():
    app.dependency_overrides[get_current_user] = _current_user_override
    try:
        # create with a secret key
        created = client.post("/models", json={
            "name": "Cloud", "provider": "openai",
            "base_url": "https://api.openai.com/v1", "model": "gpt-5", "api_key": "sk-supersecret",
        })
        assert created.status_code == 201
        body = created.json()
        assert body["has_api_key"] is True and body["is_default"] is True
        # the plaintext key must NOT appear anywhere in the response
        assert "api_key" not in body
        assert "sk-supersecret" not in created.text
        ep_id = body["id"]

        # list shows it, still no plaintext key
        listed = client.get("/models").json()
        assert len(listed) == 1 and "sk-supersecret" not in client.get("/models").text

        # unknown provider rejected by the schema validator
        assert client.post("/models", json={
            "name": "X", "provider": "totally-unknown", "base_url": "u", "model": "m",
        }).status_code == 422

        # delete
        assert client.delete(f"/models/{ep_id}").status_code == 204
        assert client.get("/models").json() == []
    finally:
        app.dependency_overrides.pop(get_current_user, None)
