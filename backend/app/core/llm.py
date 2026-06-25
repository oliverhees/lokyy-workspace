"""Multi-provider LLM layer (M1/T1.1).

Model-agnostic by design. Most providers (Ollama, vLLM, llama.cpp, LM Studio,
Mistral-EU, OpenRouter, OpenAI) speak the OpenAI Chat Completions format; Anthropic
uses its own Messages API. We normalize both behind `chat()` / `stream_chat()`.

Pure transport over httpx — no global state — so it's testable with a mock transport.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum

import httpx


class Provider(str, Enum):
    openai = "openai"  # OpenAI-compatible (covers most local + cloud providers)
    anthropic = "anthropic"


@dataclass
class LLMConfig:
    base_url: str
    model: str
    api_key: str | None = None
    provider: Provider = Provider.openai
    timeout: float = 120.0
    extra_headers: dict[str, str] = field(default_factory=dict)


class Message(dict):
    """A chat message: {"role": ..., "content": ...}. dict for easy JSON."""

    def __init__(self, role: str, content: str):
        super().__init__(role=role, content=content)


def detect_provider(base_url: str) -> Provider:
    """Heuristic provider detection from the endpoint URL."""
    u = base_url.lower()
    if "anthropic" in u:
        return Provider.anthropic
    return Provider.openai


def _headers(cfg: LLMConfig) -> dict[str, str]:
    h = {"Content-Type": "application/json", **cfg.extra_headers}
    if cfg.provider is Provider.anthropic:
        if cfg.api_key:
            h["x-api-key"] = cfg.api_key
        h.setdefault("anthropic-version", "2023-06-01")
    elif cfg.api_key:
        h["Authorization"] = f"Bearer {cfg.api_key}"
    return h


def _url(cfg: LLMConfig, *, stream: bool) -> str:
    base = cfg.base_url.rstrip("/")
    if cfg.provider is Provider.anthropic:
        return f"{base}/messages"
    return f"{base}/chat/completions"


def _payload(cfg: LLMConfig, messages: list[dict], *, stream: bool) -> dict:
    if cfg.provider is Provider.anthropic:
        sys = [m["content"] for m in messages if m["role"] == "system"]
        convo = [m for m in messages if m["role"] != "system"]
        body: dict = {"model": cfg.model, "messages": convo, "max_tokens": 4096, "stream": stream}
        if sys:
            body["system"] = "\n\n".join(sys)
        return body
    return {"model": cfg.model, "messages": messages, "stream": stream}


def _extract_content(cfg: LLMConfig, data: dict) -> str:
    if cfg.provider is Provider.anthropic:
        parts = data.get("content", [])
        return "".join(p.get("text", "") for p in parts if p.get("type") == "text")
    return data.get("choices", [{}])[0].get("message", {}).get("content", "") or ""


def _extract_delta(cfg: LLMConfig, evt: dict) -> str:
    if cfg.provider is Provider.anthropic:
        if evt.get("type") == "content_block_delta":
            return evt.get("delta", {}).get("text", "") or ""
        return ""
    return evt.get("choices", [{}])[0].get("delta", {}).get("content", "") or ""


async def chat(messages: list[dict], cfg: LLMConfig, *, client: httpx.AsyncClient | None = None) -> str:
    """Non-streaming completion. Returns the assistant text."""
    own = client is None
    client = client or httpx.AsyncClient(timeout=cfg.timeout)
    try:
        resp = await client.post(_url(cfg, stream=False), headers=_headers(cfg),
                                 json=_payload(cfg, messages, stream=False))
        resp.raise_for_status()
        return _extract_content(cfg, resp.json())
    finally:
        if own:
            await client.aclose()


async def stream_chat(messages: list[dict], cfg: LLMConfig, *,
                      client: httpx.AsyncClient | None = None) -> AsyncIterator[str]:
    """Streaming completion. Yields text deltas (SSE `data:` lines)."""
    own = client is None
    client = client or httpx.AsyncClient(timeout=cfg.timeout)
    try:
        async with client.stream("POST", _url(cfg, stream=True), headers=_headers(cfg),
                                 json=_payload(cfg, messages, stream=True)) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                payload = line[len("data:"):].strip()
                if payload in ("", "[DONE]"):
                    continue
                try:
                    delta = _extract_delta(cfg, json.loads(payload))
                except json.JSONDecodeError:
                    continue
                if delta:
                    yield delta
    finally:
        if own:
            await client.aclose()
