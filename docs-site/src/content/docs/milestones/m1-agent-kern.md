---
title: M1 — Agent-Kern
description: Funktionierender Chat-Agent mit Tools, modell-agnostisch.
---

**Ziel:** ein funktionierender, modell-agnostischer Chat-Agent mit Tool-System.

## Tasks

- **T1.1 — Multi-Provider-LLM-Layer + Streaming** ✅
  Provider-agnostischer LLM-Client (`app/core/llm.py`): OpenAI-kompatibles Format (deckt Ollama, vLLM, llama.cpp, LM Studio, Mistral-EU, OpenRouter, OpenAI) **und** Anthropic Messages API. `chat()` (non-streaming) + `stream_chat()` (SSE-Deltas), Provider-Erkennung, getypte `LLMConfig`. 4 Tests grün via httpx-MockTransport (kein echtes Modell nötig).
- **T1.2 — Agent-Loop (multi-round, Tool-Calling)** ✅
  Tool-Registry (`app/core/tools.py`) + Agent-Loop (`app/core/agent.py`): Mehrrunden-Schleife LLM→parse→execute→feed. Tool-Calls via fenced ` ```tool {json} ``` ` (provider-agnostisch, auch für kleine lokale Modelle ohne native tool-calling). Runaway-Schutz (Repeat-Detection + Max-Rounds-Cap), robuste Fehlerbehandlung (Tools crashen den Loop nie). 6 Tests grün (28 gesamt).
- **T1.3 — Tool-System + Policy/Security** ✅
  Policy/Security auf der Tool-Registry: `Tool.requires_admin`, `execute(is_admin=…)` blockt privilegierte Tools für Non-Admins (Defense-in-Depth), `schemas_for(is_admin)` versteckt sie aus dem Prompt — wie das odysseus-Trust-Modell. Builtins (`builtin_tools.py`): `current_time` (alle), `run_shell`/`run_python` (admin-only, laufen im T1.5-Sandbox). Agent-Loop reicht `is_admin` durch. 5 Tests grün (42 gesamt).
- **T1.4 — RAG-Tool-Selektion** ✅
  `ToolSelector` (`app/core/tool_selection.py`): embedding-basierte Relevanz-Auswahl (Cosine, top-k), respektiert Admin-Policy, pluggable `EmbedFn` (fastembed-Default, lokal). Nur relevante Tools in den Prompt → gegen Prompt-Bloat (wichtig für kleine Modelle). 4 Tests grün (46 gesamt). **Engineer-Entscheidung:** In-Memory-Cosine für die kleine Tool-Menge (pgvector kommt beim großen Memory/RAG-Layer in M2, wo es hingehört — dieselbe `EmbedFn`-Abstraktion).

**M1 (Agent-Kern) — Bausteine 6/6** + **Integration ✅.** LLM-Layer · Agent-Loop · Tool-System+Policy · Tool-Selektion · Sandbox · Chat-UI.

- **M1-Integration: `/chat`-Endpoint** ✅ — `app/api/chat_routes.py`: POST `/chat` als SSE-Stream (LLM-Stream wenn konfiguriert, sonst Echo-Fallback), CORS für die PWA. **End-to-End mit echtem Chrome verifiziert** (Chat-UI ↔ Backend, Status „verbunden", Backend-Antwort im Stream). Nächste Stufe: voller Agent-Loop mit Tools/Selektor im Stream + Auth-Enforcement am Endpoint.
- **T1.5 — Sandbox für Shell/Code-Tools** ✅
  Subprocess-Isolation (`app/core/sandbox.py`): async `run_shell`/`run_python`, Timeout (Prozessgruppe-SIGKILL), Output-Cap, isoliertes temp-Workdir, bereinigte Env (Allow-List), `python -I`. 9 Tests. Container/Egress als nächste Stufe. *(Parallel von Subagent gebaut.)*
- **T1.6 — Chat-UI** ✅
  Chat-Oberfläche (`app/chat/`, `components/chat/`) im Brand-Design (Cyan→Blau-Bubbles, Dark/Light, i18n DE/EN). Streaming-Client `streamChat()` gegen `POST /chat` (SSE, tolerant ggü. Plain-Text + Echo-Fallback). Build grün, **Sichtprüfung bestanden** (Senden→Streaming→Antwort + Optik). *(Parallel von Subagent gebaut.)*

## Offen / Notizen
- DB-gestützte Endpoint-/Key-Verwaltung (ModelEndpoint-Modell) folgt mit dem Agent-Loop (T1.2),
  wo Provider-Auswahl pro Session gebraucht wird.
