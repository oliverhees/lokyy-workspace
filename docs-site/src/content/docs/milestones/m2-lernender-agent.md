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
- **M2.2 — Memory (pgvector)** ✅
  Echtes Langzeitgedächtnis: `MemoryItem` pro Workspace mit **pgvector**-Embedding-Spalte (in SQLite
  JSON-Fallback für Tests). **Pluggable Embeddings** (`app/core/embeddings.py`): lokal via
  **fastembed** (Default, offline/DSGVO, multilinguales Modell `paraphrase-multilingual-MiniLM-L12-v2`,
  384 dim) oder Cloud via LiteLLM (`embedding_provider`). `memory_service`: Speichern (embed) +
  **Recall** (pgvector-Cosine in Postgres, Python-Cosine als Fallback). Jeder Chat ruft relevante
  Erinnerungen ab und hängt sie an den System-Prompt; die User-Nachricht wird für späteren Recall
  gespeichert (M2.3 verfeinert das zu extrahierten Fakten). Memory bricht den Chat nie (gekapselt).
  **Verifiziert:** 3 Tests inkl. **echtem semantischem Recall** („Kaffee" für „Welches Getränk mag ich?")
  + Workspace-Scope → 101 gesamt; Backend startet mit pgvector-Extension + Migration.
- **M2.3 — Self-Improvement** ✅
  Nach jedem Chat-Turn destilliert der Agent **dauerhafte Fakten über den Nutzer** aus dem
  Austausch (`app/core/learning_service.py`): LLM-Call mit striktem Prompt → JSON, **Pydantic-validiert**
  (`ExtractedFacts`), tolerant geparst (Müll → leere Liste). Die Fakten werden als Memory
  (`kind="fact"`) gespeichert und ersetzen die rohe Nachrichten-Speicherung aus M2.2 — der Recall
  liefert so prägnante Erkenntnisse statt roher Sätze. Komplett best-effort: bricht den Chat nie.
  **Verifiziert:** 3 Tests (Parsing: Trim/Filter/Cap, gültiges + Nicht-JSON via Mock-LLM) → 104 gesamt.
- **M2.4 — Telos-Integration** ✅
  `telos`-Feld am `AgentContext` (Mission/Ziele/Challenges als Markdown). Der Context-Assembler
  hängt es als eigenen Abschnitt an den System-Prompt mit dem Hinweis, Vorschläge an diesen Zielen
  auszurichten. Bearbeitbar im Agent-Tab (drittes Feld). Migration mit `server_default` (bestehende
  Zeilen). **Verifiziert:** Telos-Assembler-Test (+ leerer Fall) → 105 Tests grün; Sichtprüfung.

> **🚩 M2 abgeschlossen:** Der Agent hat Persona, kennt den Nutzer, erinnert sich (pgvector),
> lernt aus Gesprächen und richtet sich an den Zielen aus — alles lokal/DSGVO-konform.

## QA-Gate M2 — ✅ Conditional Pass

Dedizierter QA-Pass (analog Phase F), durchgeführt von drei Review-Agenten: **Security-Audit**,
**Coverage/Test-Lauf**, **Code-Review** (jeweils mit direktem Quell-Read, da der M2-Code nach dem
letzten Wissensgraph-Build entstand).

- **Tests real verifiziert:** **107 passed / 0 failed** gegen echtes Postgres + pgvector
  (`localhost:5435`) — der Memory-Stand „105 grün" war kein False-Positive; +2 durch die neuen
  Cross-Tenant-Regressionstests.
- **Scoping:** faktisch sauber — jeder Memory-/Context-Pfad filtert strikt auf den eigenen
  Workspace, kein realer Cross-User-Leak. Der QA-Pass deckte auf, dass die **Cross-Tenant-Isolation
  des AgentContext** bisher nur durch Code-Read, nicht durch einen Test abgesichert war (mit
  „Pass = fertig" hätte ein künftiger Refactor sie lautlos öffnen können). Geschlossen durch
  Regressionstests auf **Service- und Route-Ebene** (Commit `f3ada4c`).
- **Offene Fix-Items (Backlog, nicht-blockierend):** Embedding-Dim-Guard (cloud 1536 vs lokal 384),
  Memory-Retrieval-Schwellwert (gegen Rauschen im Prompt), Fakten-Extraktion aus dem Stream-Abschluss
  lösen (UX), SSRF-Default härten. **Prompt-Injection-Härtung** der Memory-Pipeline ist heute
  self-injection (workspace-scoped) und für geteilte Workspaces (M7) vorgemerkt.

> **🚩 Meilenstein-Haken:** M2 hat das QA-Gate **bestanden**. Details &amp; Findings in Plane `LWS-65`.
