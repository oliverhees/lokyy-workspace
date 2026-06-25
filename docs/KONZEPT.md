# Lokyy Workspace — Konzept & Architektur (lebendes Dokument)

> Status: **Planungsphase** — wird iterativ verfeinert. NICHTS hieraus wird in Plane
> als Task/Meilenstein angelegt, bis Oliver es ausdrücklich freigibt.
> Marke: **Lokyy** (korrekt: „lokyy"). Produkt: **Lokyy Workspace**.

## Vision
Self-hosted **KI-Betriebssystem** für **Selbstständige & KMU in Deutschland** — die zentrale
Plattform für die gesamte KI-gestützte Arbeit. Agenten, Projekte, Dateien, Workflows und Skills
laufen darin zusammen wie Programme auf einem OS (erweiterbar, einheitliche Oberfläche, der eine
Ort, an dem gearbeitet wird). Eigenständige Clean-Room-Reimplementierung (inspiriert von
odysseus, kein Fork). Kernversprechen: **maximal sicher, DSGVO-by-default, lokal ODER auf
eigenem Server, mit lernendem Agenten.** „Ein Selbstständiger sieht es und sagt: das muss ich haben."

## Bestätigte Grundentscheidungen
- **Architektur:** Frontend **TypeScript / Next.js (PWA)**, Backend **Python / FastAPI**. Saubere Trennung: Next.js = dünne Client-PWA, FastAPI = das einzige Backend.
- **Datenbank:** **PostgreSQL** + **pgvector** (ersetzt ChromaDB → ein System, ein Sync-Ziel, transaktionale Konsistenz Vektor+Daten).
- **Deployment:** **Docker** (Image-Parität lokal/Server). Nur self-hosted; SaaS evtl. später.
- **Zielgruppe:** Selbstständige & KMU.
- **MVP:** schmaler Killer-Kern zuerst (Build in Public). **Killer-Feature #1: selbstlernender Agent (Telos/Soul/Memory).**
- **Lizenz:** **AGPL-3.0 + CLA** (Contributor License Agreement) → offen + später kommerziell vertreibbar (Dual-License). Copyright bleibt vollständig bei uns (Clean-Room).

## Die 4 Kern-Primitive (alles baut darauf auf)
1. **Workspace** — Einheit für Sync, Sharing, Kontext. Ordner (Soul/User/Telos/Memory/Docs/Chats) + DB-Scope.
2. **Agent-/Workflow-Runtime** — Multi-Agent, Orchestrator, Skill-Chaining, Self-Improvement laufen alle auf *einer* Step-Engine (Step = Agent/Skill/Prompt mit typisiertem Input/Output, parallel/sequenziell, persistent, resumebar).
3. **Kontext-/Lern-Layer** — Telos (Miessler), Soul.md/User.md, Memory. Retrieval-basiert (NIE Full-Load).
4. **Sync-Layer** — lokal ↔ Server ↔ Mitarbeiter; drei Modi; Offline/PWA; geteilte Workspaces.

---

## Anforderungen & gewählte Lösungsansätze

### K1 — Kontext sauber halten (kritisch)
**Problem:** Soul/User/Telos/Memory dürfen den Kontext NICHT zumüllen. Keine Riesen-MD im Prompt.
**Lösung — „Context Assembler" (Tiered Retrieval):**
- **Immer geladen (winzig, ~paar hundert Token):** auto-generiertes, komprimiertes Identitäts-Briefing (Top-Fakten zu User/Agent). Wird automatisch aktuell gehalten.
- **On-Demand:** alles andere wird gechunkt + in pgvector embedded und **nur bei Relevanz** abgerufen (automatisches RAG pro Anfrage + `recall(query)`-Tool für den Agenten).
- **Telos strukturiert** in DB-Feldern statt Fließtext → gezieltes Laden einzelner Aspekte.
- **Token-Budget-Manager** + Kompaktierung alter Nachrichten.
→ Genauso gut wie odysseus' ChromaDB-Ansatz, integriert in pgvector, deterministisch klein.

### K2 — pgvector statt ChromaDB
ChromaDB-Vorteil nur bei Millionen+ Vektoren / reiner Vektor-Performance — für KMU irrelevant. pgvector gewinnt: ein Backup, ein Sync-Ziel, transaktional, HNSW-Index. **Entscheidung: pgvector.**

### K3 — Self-Improvement-Layer
Reflexions-Loop: nach Interaktionen Erkenntnisse extrahieren → Memory/User.md anreichern → künftig nutzen. Eigene Schicht über dem Agent-Loop.

### K4 — Multi-Agent / Orchestrator + Workflows + Skill-Chaining
Eine gemeinsame Runtime. Orchestrator spawnt/parallelisiert Sub-Agenten, aggregiert Ergebnisse. Workflows = Step-Ketten (Ergebnis fließt in nächsten Step). Skill-Chaining = zeitgesteuerte Workflows. Vollautomatisch → Notification „Workflow erfolgreich" + Artefakt/Chat ansehbar.

### K5 — Betriebsmodi & Sync
**Drei Modi:** (a) nur offline, (b) hybrid (lokal aktiv + Server-Sync), (c) nur remote.
Frontend spricht gegen konfigurierbare Backend-URL → Verbindungs-Switch per Button.
**Modell:** server-zentrisch + offline-fähige Clients; **Single-Writer pro Workspace** (konfliktarm).
**Auto-Sync** im Hintergrund wenn online; **Retry-Logik** (z.B. alle 15 Min) bis Sync gelingt.
**Status-UX:** „zuletzt synchronisiert vor X", Sync-Button leuchtet bei ausstehender Synchronisation.
**Edge-Case** (Rechner aus, ungesynct, unterwegs): unvermeidbar physikalisch; Mitigation = aggressives Auto-Sync + klare Warnung beim Verlassen. Konflikt beim Heimkommen → Merge (siehe K7).

### K6 — Sicherheit (Verkaufsargument #1)
Remote-Verbindungen absolut sicher (TLS, mTLS-Option, Auth-Härtung). Web-Zugriff maximal geschützt (2FA, sichere Sessions, Reverse-Proxy/Zero-Trust-Empfehlung). Secrets verschlüsselt at rest. Shell/Code-Tools in **echtem Sandbox** (odysseus-Lücke schließen).

### K7 — Geteilter Workspace + Merge (Mittelstand-Kracher)
Workspace teilbar; Mitarbeiter mit eigener Instanz/Login arbeitet im geteilten Workspace.
**Gefahr:** gleichzeitige Bearbeitung → Merge-Konflikte. Denkrahmen = GitHub.
- **v1:** Git-artiges Modell für Dateien (3-way-merge, Konfliktauflösung); strukturierte DB-Daten via optimistic locking (Versionsnummer).
- **v2:** CRDT (Yjs/Automerge) für echtes Live-Co-Editing einzelner Dokumente.

### K8 — Anonymisierungs-Layer (Ultimo-Differenzierungsmerkmal)
Zuschaltbare PII-Anonymisierung VOR LLM-Versand (global ODER pro Chat, Badge „Anonymisierung an").
Eigenbau (NICHT austrai-privacyproxy übernehmen — Referenz: github.com/flbcoat/austrai-privacyproxy).
**Pipeline:** PII-Erkennung (lokales NER + Regex/Gazetteer für **deutsche** Muster: IBAN, USt-IdNr, Steuer-ID, SV-Nr, dt. Adressen) → konsistente Pseudonyme (Mapping bleibt lokal) → De-Anonymisierung der Antwort.
Bei lokalem Modell ohnehin sicher; Layer = Zusatzschutz/Compliance-Nachweis. **Disclaimer:** kein 100%-Schutz.

### K9 — Kryptografische Signatur (eIDAS)
odysseus „Signatur" = nur Bild-Stempel (EES). Stufen:
- **v1: FES (fortgeschritten, PAdES)** — selbst baubar: kryptografisch signierte PDFs, eigenes Zertifikat/PKI, Integritätsprüfung.
- **später: QES (qualifiziert)** — braucht QTSP (z.B. D-Trust/Bundesdruckerei), Drittanbieter-Integration.

### K10 — Multi-Tenant / Firmen-Setup (von Anfang an einplanen!)
Modell: **Organisation → Users → Workspaces → Permissions**. Org-Admin (Chef) gibt Workspaces frei, lädt Mitarbeiter ein. Mitarbeiter kann mehrere Verbindungen/Profile haben (Firmen-Server + privat lokal). odysseus' Owner-Scoping = Basis → erweitern zu org/workspace-scoping.
**Geschäftsmodell:** wir installieren/managen beim Kunden (self-hosting). Begründet AGPL+CLA (K0/Lizenz).

### K11 — Artefakt-Panel (Killer-Feature, wie Claude)
Rechte Seitenleiste öffnet sich automatisch und **rendert Artefakte live**: HTML/JS-Visualisierungen, Diagramme (Mermaid/D3), Markdown, Code, Tabellen, **PDF-Preview**. odysseus hat das NICHT in dieser Form (nur Document-Editor + Research-Report). Wir bauen ein generisches Artefakt-System.
**Sicherheit:** LLM-generierter Code ist untrusted → Rendering in **sandboxed iframe** (strikte CSP), kein Zugriff auf Session/Netz.

### K12 — Nativer Datei-Editor + Verzeichnisbaum + Projekte
- **Projekte** (wie Claude Projects): Projekt = Workspace-(Unter-)Ordner + zugewiesener Kontext. Alles Erstellte landet in diesem Ordner.
- **Verzeichnisbaum** ein-/ausblendbar (wie Hermes / AionUi): zeigt, in welchem Ordner man arbeitet.
- **Datei anklicken → öffnet im Artefakt-/Editor-Panel** (CodeMirror/Monaco). Markdown & Co. **direkt editierbar**, Speichern in den Ordner. Kein Verlassen des Systems nötig.
- Verzahnt mit Workspace (Ordner) + Artefakt-Panel (K11) + Sync (Ordner wird synchronisiert).

---

## Tech-Stack & eingesetzte Systeme

> Klarstellung: odysseus basiert **NICHT** auf OpenCode — es ist ein eigener Python/FastAPI-Agent-Loop mit optionalen CLI-Integrationen (Claude Code, Codex). **Wir setzen OpenCode NICHT als Basis ein** — eigener Agent-Loop = volle Kontrolle + Lizenzfreiheit. Von OpenCode/Claude-Code-Mustern (AGENTS.md/Soul-Konzept, Tool-Design) lernen wir konzeptionell.

**Backend (Python):** FastAPI + uvicorn (API, SSE-Streaming) · SQLAlchemy/SQLModel + Alembic (ORM/Migrationen) · **PostgreSQL + pgvector** · Pydantic v2 · httpx · Worker für Workflows/Scheduler (ARQ/Celery) · MCP-SDK (Tools) · Auth: argon2/bcrypt + pyotp (2FA).
**KI/Daten:** Embeddings fastembed (lokal ONNX) / OpenAI-kompat · PII-NER lokal (spaCy de o.ä.) für Anonymisierung · PDF/Signatur PyMuPDF/pikepdf + pyhanko (PAdES/FES) · markitdown (Office) · caldav + icalendar.
**Frontend (TypeScript):** Next.js (App Router, PWA via Serwist) · React + Tailwind + shadcn/ui · TanStack Query · CodeMirror/Monaco (Editor) · sandboxed iframe + Mermaid/D3 (Artefakte).
**Infra:** Docker + Compose · Reverse-Proxy Caddy/Traefik (TLS) · optional Tailscale/WireGuard (sichere Remote-Verbindung).
**Sync:** v1 Git-artig (libgit2/isomorphic-git) · v2 CRDT (Yjs/Automerge).
**LLM-Provider (modell-agnostisch):** lokal (Ollama/vLLM/llama.cpp) + Cloud (Anthropic, OpenAI, Mistral-EU, Aleph Alpha, IONOS, OpenRouter).

---

## Brand & Design (K13)
**Logo:** geometrischer Drachenkopf mit **Cyan→Blau-Verlauf** (`assets/brand/lokyy-logo.png`). Das gesamte Design richtet sich danach.
**Prinzip:** modern, clean, **geometrisch-kantig** (wie das Logo), vertrauenswürdig — NICHT altbacken. Viel Weißraum, klare Hierarchie. Gradient als wiederkehrendes Markensignal. Tech-Vertrauen + Datensicherheit visuell.

**Markenfarben (aus dem Logo):**
- **Cyan (Highlight):** ~`#22D3EE` (Tailwind cyan-400)
- **Blau (Primär):** ~`#2563EB` (blue-600)
- **Deep Blue (Akzent):** ~`#1D4ED8` (blue-700)
- **Signature-Gradient:** linear Cyan-400 → Blue-600 (Logo, Primär-Buttons, Akzent-Highlights)
- **Neutrale:** **Slate** (kühl, harmoniert mit Blau) statt warmer Grautöne

**Light Mode:** BG `#F8FAFC` (slate-50) / Flächen `#FFFFFF` · Text `#0F172A` (slate-900) · Muted slate-500 · Primär blue-600 (Hover blue-700) · Gradient sparsam für Highlights.
**Dark Mode:** BG `#0B1120` (dunkles Navy, nicht reines Schwarz) · Flächen `#111827`/slate-900 · Text `#E2E8F0` · Muted slate-400 · Akzent blue-500 + Cyan-Glow · Gradient leuchtet auf dunklem Grund.

- **UI-Basis:** **Tailwind** + shadcn/ui (moderne, neutrale Komponenten, moderate Rundungen, dezente Schatten), Light + Dark Mode.
- **Typografie:** Inter (UI) + Geist Mono (Code).
- **Wortmarke:** „lokyy" (kleingeschrieben) — moderne Lowercase-Marke, Drachenkopf als Icon-Mark.
- **Tonalität:** direkt, kompetent, deutsch, nahbar.
- **Mockups (interaktiv, Light/Dark):** `docs/mockups/lokyy-mockup.html` (Chat-Ansicht) · `docs/mockups/lokyy-dashboard.html` (Dashboard) — echtes HTML/Tailwind, Grundlage des späteren Frontends. Screenshots daneben.
- **To-do:** Hex-Werte final am Logo kalibrieren.

---

## Offene Designfragen (zu klären)
- Markenfarbe + finales Brand-Konzept (siehe K13).
- DE-Provider-Matrix v1 (LLM: Aleph Alpha/IONOS/Mistral-EU? Mail/CalDAV: mailbox.org/Posteo/Nextcloud?).
- Sandbox-Technologie für Shell/Code-Tools.
- Genauer Sync-Mechanismus v1 (Git-artig vs. eigene Engine).
