"""Chat endpoint (F5): real model, persisted sessions, SSE streaming.

POST /chat {session_id, content} (auth required, owner-scoped):
  1. persist the user message into the session (+ auto-title on first message)
  2. stream the assistant reply from the user's DEFAULT model endpoint (F4),
     via the LiteLLM layer (F4.1)
  3. persist the full assistant message once the stream completes

If no model is configured, a friendly hint is streamed instead of a model call.
The assistant message is persisted from a fresh DB session inside the generator,
because the request-scoped session may already be closed while streaming.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import llm, model_service, session_service
from app.core.db import engine, get_session
from app.models.entities import User

router = APIRouter(tags=["chat"])


class ChatIn(BaseModel):
    session_id: str
    content: str


def _sse(delta: str) -> str:
    return f"data: {json.dumps({'delta': delta})}\n\n"


async def _hint_stream(text: str) -> AsyncIterator[str]:
    yield _sse(text)
    yield "data: [DONE]\n\n"


def _persist_assistant(session_id: str, text: str, model_used: str | None) -> None:
    with Session(engine) as s:
        session_service.add_message(s, session_id=session_id, role="assistant",
                                    content=text, model_used=model_used)


async def _llm_stream(history: list[dict], cfg: llm.LLMConfig, session_id: str) -> AsyncIterator[str]:
    full = ""
    try:
        async for delta in llm.stream_chat(history, cfg):
            full += delta
            yield _sse(delta)
    except Exception as exc:  # surface a friendly error, never crash the stream
        yield _sse(f"[LLM-Fehler: {exc}]")
    if full:
        _persist_assistant(session_id, full, cfg.model)
    yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(body: ChatIn, db: Session = Depends(get_session),
               user: User = Depends(get_current_user)) -> StreamingResponse:
    session = session_service.get_owned_session(db, user_id=user.id, session_id=body.session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "session not found")

    session_service.add_message(db, session_id=session.id, role="user", content=body.content)
    session_service.maybe_autotitle(db, session=session, first_user_message=body.content)

    history = [
        {"role": m.role, "content": m.content}
        for m in session_service.list_messages(db, user_id=user.id, session_id=session.id)
    ]

    endpoint = model_service.get_default(db, user_id=user.id)
    if endpoint is None:
        return StreamingResponse(
            _hint_stream("Kein Modell konfiguriert. Lege in den Einstellungen unter „Modelle“ "
                         "einen Endpoint an, um den Chat zu nutzen."),
            media_type="text/event-stream",
        )

    cfg = llm.LLMConfig(
        base_url=endpoint.base_url,
        model=endpoint.model,
        api_key=model_service.decrypt_key(endpoint) or None,
        provider=endpoint.provider,
    )
    return StreamingResponse(_llm_stream(history, cfg, session.id), media_type="text/event-stream")
