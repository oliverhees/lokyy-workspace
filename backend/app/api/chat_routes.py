"""Chat endpoint — wires the agent stack to the UI via SSE (M1 integration).

POST /chat streams assistant text deltas as Server-Sent Events:
    data: {"delta": "Hallo"}\n\n
    data: [DONE]\n\n

If an LLM is configured (settings.llm_base_url + llm_model) it streams from the
multi-provider LLM layer (T1.1). Otherwise it falls back to an echo stream so the
end-to-end UI↔backend flow works in dev/demo without a model.

Scope note: this first integration streams the LLM directly. The full agent loop
(T1.2) with tool selection (T1.4) + tool execution (T1.3) is the next stage — it needs
per-round streaming of tool steps. Auth (T0.4) is also still to be enforced here.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core import llm
from app.core.config import get_settings

router = APIRouter(tags=["chat"])
settings = get_settings()


class ChatMessageIn(BaseModel):
    role: str
    content: str


class ChatIn(BaseModel):
    messages: list[ChatMessageIn]


def _sse(delta: str) -> str:
    return f"data: {json.dumps({'delta': delta})}\n\n"


async def _echo_stream(text: str) -> AsyncIterator[str]:
    for token in text.split(" "):
        yield _sse(token + " ")
    yield "data: [DONE]\n\n"


async def _llm_stream(messages: list[ChatMessageIn]) -> AsyncIterator[str]:
    cfg = llm.LLMConfig(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key or None,
        provider=llm.detect_provider(settings.llm_base_url),
    )
    try:
        async for delta in llm.stream_chat([m.model_dump() for m in messages], cfg):
            yield _sse(delta)
    except Exception as exc:  # surface a friendly error, never crash the stream
        yield _sse(f"[LLM-Fehler: {exc}]")
    yield "data: [DONE]\n\n"


def _llm_configured() -> bool:
    return bool(settings.llm_base_url and settings.llm_model)


@router.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    if _llm_configured():
        stream = _llm_stream(body.messages)
    else:
        last_user = next((m.content for m in reversed(body.messages) if m.role == "user"), "")
        stream = _echo_stream(f"Echo: {last_user}")
    return StreamingResponse(stream, media_type="text/event-stream")
