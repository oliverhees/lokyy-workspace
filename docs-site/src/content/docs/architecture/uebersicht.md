---
title: Architektur-Überblick
description: Die vier Kern-Primitive und der Tech-Stack von Lokyy Workspace.
---

Lokyy baut auf **vier Kern-Primitiven** auf — alles andere ist Komposition.

1. **Workspace** — Einheit für Sync, Sharing und Kontext (Ordner + DB-Scope).
2. **Agent-/Workflow-Runtime** — Multi-Agent, Orchestrator, Skill-Chaining, Self-Improvement auf einer Step-Engine.
3. **Kontext-/Lern-Layer** — Telos, Soul.md/User.md, Memory; retrieval-basiert (kein Kontext-Müll).
4. **Sync-Layer** — lokal ⇆ Server ⇆ Mitarbeiter; drei Modi; Offline/PWA.

## Tech-Stack

| Schicht | Technologie |
|---------|-------------|
| Frontend | TypeScript · Next.js (PWA) · Tailwind · shadcn/ui |
| Backend | Python · FastAPI |
| Datenbank | PostgreSQL + pgvector |
| Infra | Docker |
| LLM | modell-agnostisch (lokal + Cloud, EU-Provider) |

Die vollständige Architektur liegt im Repo unter `docs/KONZEPT.md`, die Projektbeschreibung unter `docs/PROJEKTBESCHREIBUNG.md`.
