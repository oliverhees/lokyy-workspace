"""M1 integration: /chat endpoint streams SSE (echo fallback when no LLM configured)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_streams_echo_sse():
    resp = client.post("/chat", json={"messages": [{"role": "user", "content": "Hallo Welt"}]})
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    body = resp.text
    assert "Echo:" in body
    assert "Hallo" in body and "Welt" in body
    assert "[DONE]" in body


def test_chat_empty_messages_ok():
    resp = client.post("/chat", json={"messages": []})
    assert resp.status_code == 200
    assert "[DONE]" in resp.text
