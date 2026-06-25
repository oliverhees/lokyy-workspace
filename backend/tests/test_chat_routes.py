"""F5: /chat — auth, no-model hint, and real streaming + persistence (mocked LLM)."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
import app.api.chat_routes as chat_routes
from app.api.deps import get_current_user
from app.core import auth, model_service, session_service
from app.core.db import get_session
from app.main import app
from app.models.entities import User

_eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(_eng)

with Session(_eng) as _s:
    _user = auth.signup(_s, organization_name="Acme", email="c@x.de",
                        password="pw123456", display_name="C")
    _USER_ID = _user.id


def _session_override():
    with Session(_eng) as s:
        yield s


def _cu() -> User:
    with Session(_eng) as s:
        return s.get(User, _USER_ID)


client = TestClient(app)


@pytest.fixture(autouse=True)
def _override_session():
    # set per-test so it never leaks into other modules' route tests
    app.dependency_overrides[get_session] = _session_override
    yield
    app.dependency_overrides.pop(get_session, None)


def test_chat_requires_auth():
    assert client.post("/chat", json={"session_id": "x", "content": "hi"}).status_code == 401


def test_chat_no_model_streams_hint():
    # runs before any model is created (file order) → exercises the no-model path
    app.dependency_overrides[get_current_user] = _cu
    try:
        with Session(_eng) as s:
            sess = session_service.create_session(s, user=s.get(User, _USER_ID))
            sid = sess.id
        r = client.post("/chat", json={"session_id": sid, "content": "hallo"})
        assert r.status_code == 200
        assert "Kein Modell konfiguriert" in r.text and "[DONE]" in r.text
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_chat_streams_and_persists(monkeypatch):
    app.dependency_overrides[get_current_user] = _cu
    monkeypatch.setattr(chat_routes, "engine", _eng)  # persist into the test DB

    seen = {}

    async def fake_stream(history, cfg):
        seen["history"] = history
        for d in ["Hal", "lo"]:
            yield d

    monkeypatch.setattr(chat_routes.llm, "stream_chat", fake_stream)
    try:
        with Session(_eng) as s:
            u = s.get(User, _USER_ID)
            model_service.create_endpoint(s, user_id=u.id, name="M", provider="openai",
                                          base_url="http://127.0.0.1:9/v1", model="m", api_key="k")
            sess = session_service.create_session(s, user=u)
            sid = sess.id
        r = client.post("/chat", json={"session_id": sid, "content": "hallo"})
        assert r.status_code == 200
        assert "Hal" in r.text and "lo" in r.text and "[DONE]" in r.text
        # both user and assistant messages persisted
        with Session(_eng) as s:
            msgs = session_service.list_messages(s, user_id=_USER_ID, session_id=sid)
        by_role = {m.role: m.content for m in msgs}
        assert by_role.get("user") == "hallo"
        assert by_role.get("assistant") == "Hallo"  # accumulated from deltas
        # M2.1: the system prompt (persona) is prepended to what the model sees
        assert seen["history"][0]["role"] == "system"
        assert "Lokyy" in seen["history"][0]["content"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_chat_foreign_session_404():
    app.dependency_overrides[get_current_user] = _cu
    try:
        assert client.post("/chat", json={"session_id": "nonexistent", "content": "x"}).status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)
