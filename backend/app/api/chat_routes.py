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
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import context_service, llm, memory_service, model_service, session_service, ssrf
from app.core.config import get_settings
from app.core.db import engine, get_session
from app.models.entities import User

router = APIRouter(tags=["chat"])
log = logging.getLogger("lokyy.chat")


class ChatIn(BaseModel):
    session_id: str
    content: str
    model_endpoint_id: str | None = None  # optional override; falls back to the default


def _sse(delta: str) -> str:
    return f"data: {json.dumps({'delta': delta})}\n\n"


async def _hint_stream(text: str) -> AsyncIterator[str]:
    yield _sse(text)
    yield "data: [DONE]\n\n"


def _persist_assistant(session_id: str, text: str, model_used: str | None) -> None:
    try:
        with Session(engine) as s:
            session_service.add_message(s, session_id=session_id, role="assistant",
                                        content=text, model_used=model_used)
    except Exception:  # never lose the answer silently — at least log it
        log.exception("failed to persist assistant message for session %s", session_id)


async def _llm_stream(history: list[dict], cfg: llm.LLMConfig, session_id: str) -> AsyncIterator[str]:
    full = ""
    try:
        async for delta in llm.stream_chat(history, cfg):
            full += delta
            yield _sse(delta)
    except Exception:  # surface a generic error (no raw exception → no info leak)
        log.exception("LLM stream failed for session %s", session_id)
        yield _sse("[Fehler bei der Modell-Antwort. Bitte erneut versuchen.]")
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

    # M2.1/M2.2: system prompt = persona + profile + recalled memories for this workspace.
    ctx = context_service.get_or_create_context(db, workspace_id=session.workspace_id)
    memories: list[str] = []
    try:
        recalled = memory_service.search_memories(
            db, workspace_id=session.workspace_id, query=body.content, k=4
        )
        memories = [m.content for m in recalled]
        # remember the user's message for future recall (M2.3 will refine to facts)
        memory_service.add_memory(db, workspace_id=session.workspace_id, content=body.content)
    except Exception:  # memory must never break the chat
        log.exception("memory recall/store failed for session %s", session.id)
    system_prompt = context_service.assemble_system_prompt(ctx, memories=memories)
    history: list[dict] = [{"role": "system", "content": system_prompt}]
    history += [
        {"role": m.role, "content": m.content}
        for m in session_service.list_messages(db, user_id=user.id, session_id=session.id)
    ]

    endpoint = model_service.resolve_endpoint(db, user_id=user.id, endpoint_id=body.model_endpoint_id)
    if endpoint is None:
        return StreamingResponse(
            _hint_stream("Kein Modell konfiguriert. Lege in den Einstellungen unter „Modelle“ "
                         "einen Endpoint an, um den Chat zu nutzen."),
            media_type="text/event-stream",
        )

    # SSRF guard: the stored base_url is hit server-side during streaming.
    if endpoint.base_url:
        try:
            ssrf.validate_outbound_url(
                endpoint.base_url, allow_private=get_settings().allow_private_model_hosts
            )
        except ssrf.UnsafeUrlError:
            return StreamingResponse(
                _hint_stream("Die Base-URL des Modells ist nicht erlaubt (interne Adresse). "
                             "Bitte in den Einstellungen korrigieren."),
                media_type="text/event-stream",
            )

    cfg = llm.LLMConfig(
        base_url=endpoint.base_url,
        model=endpoint.model,
        api_key=model_service.decrypt_key(endpoint) or None,
        provider=endpoint.provider,
    )
    return StreamingResponse(_llm_stream(history, cfg, session.id), media_type="text/event-stream")
