"""T1.1: multi-provider LLM layer — OpenAI-compatible + Anthropic, chat + streaming.

Uses httpx.MockTransport, so no real model server is required.
"""
import json

import httpx

from app.core.llm import LLMConfig, Message, Provider, chat, detect_provider, stream_chat


def test_detect_provider():
    assert detect_provider("https://api.anthropic.com") is Provider.anthropic
    assert detect_provider("http://localhost:11434/v1") is Provider.openai
    assert detect_provider("https://openrouter.ai/api/v1") is Provider.openai


async def test_chat_openai_compatible():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path.endswith("/chat/completions")
        assert req.headers["Authorization"] == "Bearer k"
        body = json.loads(req.content)
        assert body["model"] == "test-model" and body["stream"] is False
        return httpx.Response(200, json={"choices": [{"message": {"content": "Hallo Welt"}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        cfg = LLMConfig(base_url="http://x/v1", model="test-model", api_key="k")
        assert await chat([Message("user", "hi")], cfg, client=client) == "Hallo Welt"


async def test_chat_anthropic():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path.endswith("/messages")
        assert req.headers["x-api-key"] == "k"
        assert req.headers["anthropic-version"]
        body = json.loads(req.content)
        assert body["system"] == "be nice"  # system extracted
        return httpx.Response(200, json={"content": [{"type": "text", "text": "Hi"}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        cfg = LLMConfig(base_url="https://api.anthropic.com/v1", model="claude",
                        api_key="k", provider=Provider.anthropic)
        msgs = [Message("system", "be nice"), Message("user", "hi")]
        assert await chat(msgs, cfg, client=client) == "Hi"


async def test_stream_chat_openai():
    def handler(req: httpx.Request) -> httpx.Response:
        chunks = (
            'data: {"choices":[{"delta":{"content":"Hal"}}]}\n'
            'data: {"choices":[{"delta":{"content":"lo"}}]}\n'
            "data: [DONE]\n"
        )
        return httpx.Response(200, content=chunks)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        cfg = LLMConfig(base_url="http://x/v1", model="m")
        out = [d async for d in stream_chat([Message("user", "hi")], cfg, client=client)]
        assert "".join(out) == "Hallo"
