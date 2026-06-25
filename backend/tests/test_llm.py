"""M1/T1.1 + F4.1: multi-provider LLM layer on LiteLLM (mapping + mocked calls).

Uses LiteLLM's built-in mock_response, so no real model server is required.
"""
from app.core import llm


def test_litellm_model_routing():
    assert llm.litellm_model("openai", "gpt-5") == "openai/gpt-5"
    assert llm.litellm_model("anthropic", "claude-sonnet-4") == "anthropic/claude-sonnet-4"
    assert llm.litellm_model("openrouter", "x/y") == "openrouter/x/y"
    # custom (self-hosted / OpenAI-API standard) routes via the OpenAI-compatible path
    assert llm.litellm_model("custom", "my-model") == "openai/my-model"


def test_build_kwargs_openai_compatible():
    cfg = llm.LLMConfig(base_url="https://openrouter.ai/api/v1", model="m",
                        api_key="sk-1", provider="openrouter")
    kw = llm.build_kwargs(cfg, [{"role": "user", "content": "hi"}], stream=True)
    assert kw["model"] == "openrouter/m"
    assert kw["api_base"] == "https://openrouter.ai/api/v1"
    assert kw["api_key"] == "sk-1"
    assert kw["stream"] is True


def test_build_kwargs_custom_uses_openai_path_with_base_url():
    cfg = llm.LLMConfig(base_url="http://localhost:8080/v1", model="local-llm", provider="custom")
    kw = llm.build_kwargs(cfg, [], stream=False)
    assert kw["model"] == "openai/local-llm"
    assert kw["api_base"] == "http://localhost:8080/v1"
    assert "api_key" not in kw  # none configured (e.g. local)


def test_detect_provider():
    assert llm.detect_provider("https://api.anthropic.com") == "anthropic"
    assert llm.detect_provider("https://openrouter.ai/api/v1") == "openrouter"
    assert llm.detect_provider("http://localhost:11434") == "ollama"
    assert llm.detect_provider("https://api.openai.com/v1") == "openai"


async def test_chat_returns_text_via_mock():
    cfg = llm.LLMConfig(base_url="http://x/v1", model="m", api_key="k", provider="openai")
    out = await llm.chat([{"role": "user", "content": "hi"}], cfg, mock_response="Hallo Welt")
    assert out == "Hallo Welt"


async def test_stream_chat_yields_deltas_via_mock():
    cfg = llm.LLMConfig(base_url="http://x/v1", model="m", api_key="k", provider="openai")
    chunks = []
    async for d in llm.stream_chat([{"role": "user", "content": "hi"}], cfg, mock_response="Stream Text"):
        chunks.append(d)
    assert "".join(chunks) == "Stream Text"
