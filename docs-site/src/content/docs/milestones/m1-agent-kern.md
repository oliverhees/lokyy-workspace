---
title: M1 — Agent-Kern
description: Funktionierender Chat-Agent mit Tools, modell-agnostisch.
---

**Ziel:** ein funktionierender, modell-agnostischer Chat-Agent mit Tool-System.

## Tasks

- **T1.1 — Multi-Provider-LLM-Layer + Streaming** ✅
  Provider-agnostischer LLM-Client (`app/core/llm.py`): OpenAI-kompatibles Format (deckt Ollama, vLLM, llama.cpp, LM Studio, Mistral-EU, OpenRouter, OpenAI) **und** Anthropic Messages API. `chat()` (non-streaming) + `stream_chat()` (SSE-Deltas), Provider-Erkennung, getypte `LLMConfig`. 4 Tests grün via httpx-MockTransport (kein echtes Modell nötig).
- **T1.2 — Agent-Loop (multi-round, Tool-Calling)** ⬜
- **T1.3 — Tool-System + Policy/Security** ⬜
- **T1.4 — RAG-Tool-Selektion via pgvector** ⬜
- **T1.5 — Sandbox für Shell/Code-Tools** ⬜
- **T1.6 — Chat-UI** ⬜

## Offen / Notizen
- DB-gestützte Endpoint-/Key-Verwaltung (ModelEndpoint-Modell) folgt mit dem Agent-Loop (T1.2),
  wo Provider-Auswahl pro Session gebraucht wird.
