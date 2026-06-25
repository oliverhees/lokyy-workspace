# Lokyy Workspace — Umsetzungsplan (Entwurf zur Review)

> **Status: ENTWURF.** Wird NICHT in Plane angelegt, bis Oliver „go" sagt.
> Struktur: **Meilensteine** = Plane-Module · **Tasks** = Plane-Issues.
> MVP = **M0 + M1 + M2** (schmaler Killer-Kern: selbstlernender Agent).
> Grundlage: `docs/KONZEPT.md`, `docs/PROJEKTBESCHREIBUNG.md`.

## Build-Reihenfolge (Überblick)
**MVP:** M0 Fundament → M1 Agent-Kern → M2 Lernender Agent (Killer-Feature).
**Danach:** M3 Projekte/Editor/Artefakte → M4 Workflows/Multi-Agent → M5 DSGVO/Security →
M6 Produktiv-Suite → M7 Sync/Team → M8 Brand/Launch.

---

## M0 — Fundament & Setup
*Ziel: lauffähiges Skelett (Backend+Frontend+DB+Auth) in Docker, lokal startbar.*
- T0.1 Monorepo-Setup (`backend/` FastAPI, `frontend/` Next.js), Lizenz **AGPL-3.0 + CLA**, README, .gitignore, Secret-Hygiene.
- T0.2 Docker Compose: FastAPI + PostgreSQL+pgvector; `.env`-Schema.
- T0.3 DB-Fundament (SQLAlchemy/SQLModel + Alembic): User, Organisation, Workspace, Session, Message — durchgängiges **owner/org-scoping**.
- T0.4 Auth: Sessions (argon2), 2FA (pyotp), API-Tokens, Login/Registrierung.
- T0.5 Next.js-PWA-Grundgerüst (Tailwind + shadcn/ui), **konfigurierbare Backend-URL** (Verbindungs-Switch lokal/server vorbereitet).
- T0.6 CI (Lint, Tests, compile-check), Test-Grundgerüst.

## M1 — Agent-Kern
*Ziel: funktionierender Chat-Agent mit Tools, modell-agnostisch.*
- T1.1 Multi-Provider-LLM-Layer (lokal: Ollama/vLLM/llama.cpp; Cloud: Anthropic/OpenAI/Mistral-EU…), Endpoint-/Key-Resolver, Streaming (SSE).
- T1.2 Agent-Loop (multi-round, Tool-Calling: fenced **und** native), Stop-/Runaway-Schutz.
- T1.3 Tool-System: Schemas, Registry, Execution, **Policy/Security** (admin/non-admin, owner-scope).
- T1.4 **RAG-Tool-Selektion** via pgvector (nur relevante Tools im Prompt).
- T1.5 **Sandbox** für Shell/Code-Tools (Container/Isolierung + Egress-Kontrolle) — odysseus-Lücke schließen.
- T1.6 Chat-UI (Streaming, Verlauf, Sessions).

## M2 — Lernender Agent (MVP-Killer-Feature)
*Ziel: Agent kennt den Nutzer, hält Kontext sauber, verbessert sich.*
- T2.1 **Workspace-Primitiv** (Ordner + DB-Scope) als Kern-Einheit.
- T2.2 **Telos** (strukturiert in DB) + `Soul.md`/`User.md` im Workspace.
- T2.3 **Memory** (pgvector): Speicherung, Retrieval, goal-based Extraction.
- T2.4 **Context Assembler** (Tiered Retrieval): Mini-Identitäts-Briefing immer + On-Demand-Retrieval + Token-Budget → kein Kontext-Müll.
- T2.5 **Self-Improvement-Loop**: Reflexion nach Interaktionen → Memory/User.md anreichern.

## M3 — Projekte, Dateibaum, Editor, Artefakte
*Ziel: voller In-System-Arbeitsplatz.*
- T3.1 **Projekte** (wie Claude Projects): Ordner-Zuweisung, projektgebundener Kontext.
- T3.2 **Verzeichnisbaum** (ein-/ausblendbar) + Datei-Operationen.
- T3.3 **Nativer Editor** (CodeMirror/Monaco), Markdown direkt editierbar, Speichern in Ordner.
- T3.4 **Artefakt-Panel** (rechte Seitenleiste): Live-Render Visualisierung/Diagramm/PDF/Code/Tabelle in **sandboxed iframe**.

## M4 — Workflows & Multi-Agent
*Ziel: Automatisierung & Orchestrierung.*
- T4.1 **Workflow-/Step-Engine** (Step = Agent/Skill/Prompt, typisierter I/O, persistent, resumebar).
- T4.2 **Orchestrator-Agent** (Sub-Agenten spawnen, **parallel**, Ergebnis-Aggregation).
- T4.3 **Skill-System** (user-editierbar) + **Skill-Chaining**.
- T4.4 **Scheduler** (zeitgesteuert, croniter) + **Notifications** („Workflow erfolgreich" + Artefakt).

## M5 — DSGVO & Sicherheit (Differenzierung)
*Ziel: „muss ich haben"-Argumente für DE.*
- T5.1 **Anonymisierungs-Layer** (PII-NER + deutsche Muster: IBAN/USt-IdNr/Steuer-ID/SV-Nr/Adressen), global/pro-Chat-Toggle, Badge, Disclaimer.
- T5.2 **Kryptografische Signatur** (PAdES/FES, eigenes Zertifikat) statt Bild-Stempel.
- T5.3 Security-Härtung: TLS/mTLS-Option, Secret-Verschlüsselung, Prompt-Injection-Wrapper, Audit.

## M6 — Produktiv-Suite (DE-Provider)
*Ziel: Knowledge-Worker-Features mit deutschen Providern.*
- T6.1 **E-Mail** (IMAP/SMTP + OAuth; mailbox.org/Posteo/Telekom), Triage/Summary/Reply — **DE-lokalisiert**.
- T6.2 **Kalender & Kontakte** (CalDAV/CardDAV; Nextcloud/mailbox.org/Posteo).
- T6.3 **Dokumente** (markitdown, PDF-Forms).
- T6.4 **Notizen & Tasks**.

## M7 — Sync & Team
*Ziel: lokal↔server↔Mitarbeiter.*
- T7.1 **Sync-Engine v1** (Git-artig, Single-Writer, Auto-Sync + Retry-Logik, Status-UX).
- T7.2 **3 Betriebsmodi** (offline / hybrid / remote), Verbindungs-Switch.
- T7.3 **Geteilte Workspaces** + Merge (3-way für Dateien, optimistic locking für DB).
- T7.4 **Multi-Tenant** (Org → Mitarbeiter → Workspaces, Freigaben/Permissions).
- T7.5 **PWA-Vertiefung** (mobil, Offline, Spracheingabe).

## M8 — Brand, Polish & Launch
*Ziel: marktreif, Build-in-Public-Launch.*
- T8.1 **Brand-Konzept** (Markenfarbe, Logo/Wortmarke „lokyy", finale UI-Politur).
- T8.2 **Onboarding** + Erststart-Flow.
- T8.3 **Barrierefreiheit** (BFSG) + Dokumentation.
- T8.4 Launch-Vorbereitung (Demo, Repo-Politur, Build-in-Public-Material).

---

## Hinweise
- Granularität hier = Meilenstein + Haupt-Tasks. Bei Plane-Anlage werden Tasks ggf. weiter in Sub-Tasks zerlegt.
- Reihenfolge ist Vorschlag — einzelne Tasks aus M5/M6 können bei Bedarf vorgezogen werden (z. B. Anonymisierung früh als Build-in-Public-Highlight).
- Querschnitt (durchgängig, kein eigener Meilenstein): Tests, Sicherheit, DE-Lokalisierung.
