---
title: M2 — Lernender Agent
description: Personalisierter, selbstlernender Agent — Kontext, Memory, Self-Improvement, Telos.
sidebar:
  order: 3
---

**Ziel:** ein Agent, der den Nutzer kennt, eine Persona hat und über die Zeit dazulernt.
Baut auf der Fundament-Phase (F) auf. Vertikale Slices, jeder für sich erlebbar.

## Tasks

- **M2.1 — Kontext-Layer (Soul + Nutzerprofil)** ✅
  Pro Workspace ein `AgentContext`: **Soul** (Persona/Verhalten) + **Nutzerprofil** (was der Agent
  über dich weiß), als Markdown in der DB. Ein **Context-Assembler**
  (`app/core/context_service.py`) baut daraus den **System-Prompt**, der jedem `/chat`-Call
  vorangestellt wird. Bearbeitbar im neuen Settings-Tab **„Agent"**. API `GET/PUT /context`
  (owner-scoped über den Default-Workspace). Sinnvolle Default-Soul für frische Workspaces.
  **Verifiziert:** 5 Tests (Service: get-or-create/Default-Soul, Update, Assembler;
  Route: Auth + Round-Trip) + Chat-Test bestätigt System-Prompt im Verlauf (→ 98 gesamt);
  Sichtprüfung des Agent-Tabs. Der Context-Assembler ist die Andockstelle für M2.2/M2.4.
- **M2.2 — Memory (pgvector)** ⏳ Embedding + Ähnlichkeitssuche → relevante Erinnerungen in den Kontext.
- **M2.3 — Self-Improvement** ⏳ Fakten aus Gesprächen ins Profil/Memory (Pydantic-validiert).
- **M2.4 — Telos-Integration** ⏳ Mission/Ziele/Challenges als Kontext.
