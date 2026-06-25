"""Multi-provider LLM layer (M1/T1.1, rebuilt on LiteLLM in F4.1).

Model-agnostic by design. LiteLLM normalizes 100+ providers behind one API and one
response shape, so we no longer hand-roll per-provider HTTP/parsing. Adding a provider
is a config/preset change, not new transport code.

Routing rule: every provider is addressed as `"<provider>/<model>"`. "custom" maps to
the OpenAI-compatible path (`openai/<model>` + api_base) — that covers self-hosted and
any OpenAI-API-standard endpoint. A base_url, when set, is passed as `api_base` and
overrides the provider default (needed for OpenRouter-style and local endpoints).

`chat()` / `stream_chat()` keep their previous shapes so the agent loop (which takes an
injected caller) and the chat route need no structural changes.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import litellm

# Curated provider ids. Most are OpenAI-compatible; LiteLLM knows their defaults.
# "custom" = any OpenAI-API-standard endpoint (self-hosted / unlisted) via api_base.
KNOWN_PROVIDERS = {
    "openai",
    "anthropic",
    "openrouter",
    "groq",
    "mistral",
    "deepseek",
    "together_ai",
    "gemini",
    "ollama",
    "azure",
    "custom",
}


class Provider(str):
    """Provider id (free string; validated against KNOWN_PROVIDERS at the edges)."""


@dataclass
class LLMConfig:
    base_url: str
    model: str
    api_key: str | None = None
    provider: str = "openai"
    timeout: float = 120.0
    extra_headers: dict[str, str] = field(default_factory=dict)


class Message(dict):
    """A chat message: {"role": ..., "content": ...}."""

    def __init__(self, role: str, content: str):
        super().__init__(role=role, content=content)


def detect_provider(base_url: str) -> str:
    """Best-effort provider id from an endpoint URL (used for legacy/auto configs)."""
    u = (base_url or "").lower()
    if "anthropic" in u:
        return "anthropic"
    if "openrouter" in u:
        return "openrouter"
    if "groq" in u:
        return "groq"
    if "mistral" in u:
        return "mistral"
    if "deepseek" in u:
        return "deepseek"
    if "11434" in u or "ollama" in u:
        return "ollama"
    return "openai"


def litellm_model(provider: str, model: str) -> str:
    """Map our (provider, model) to a LiteLLM model string."""
    if provider == "custom":
        return f"openai/{model}"  # OpenAI-API-standard, addressed via api_base
    return f"{provider}/{model}"


def build_kwargs(cfg: LLMConfig, messages: list[dict], *, stream: bool) -> dict:
    """Translate an LLMConfig into LiteLLM acompletion kwargs (pure — unit-testable)."""
    kwargs: dict = {
        "model": litellm_model(cfg.provider, cfg.model),
        "messages": messages,
        "stream": stream,
        "timeout": cfg.timeout,
    }
    if cfg.base_url:
        kwargs["api_base"] = cfg.base_url
    key = cfg.api_key
    if not key and kwargs["model"].startswith("openai/"):
        # Local / self-hosted OpenAI-compatible endpoints often need no auth, but
        # LiteLLM still requires an api_key to be present — pass a harmless placeholder.
        key = "sk-no-key-required"
    if key:
        kwargs["api_key"] = key
    if cfg.extra_headers:
        kwargs["extra_headers"] = cfg.extra_headers
    return kwargs


async def chat(messages: list[dict], cfg: LLMConfig, **litellm_overrides) -> str:
    """Non-streaming completion. Returns the assistant text.

    `litellm_overrides` are forwarded to LiteLLM (e.g. `mock_response=...` in tests).
    """
    kwargs = build_kwargs(cfg, messages, stream=False) | litellm_overrides
    resp = await litellm.acompletion(**kwargs)
    return resp.choices[0].message.content or ""


async def stream_chat(messages: list[dict], cfg: LLMConfig, **litellm_overrides) -> AsyncIterator[str]:
    """Streaming completion. Yields text deltas."""
    kwargs = build_kwargs(cfg, messages, stream=True) | litellm_overrides
    resp = await litellm.acompletion(**kwargs)
    async for chunk in resp:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
