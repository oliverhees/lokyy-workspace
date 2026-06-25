# Lokyy Workspace — Projektregeln (verbindlich)

> Eigenständiger, self-hosted **Agent Workspace für den deutschen Markt**.
> Inspiriert von [odysseus](https://github.com/pewdiepie-archdaemon/odysseus) (AGPL-3.0) —
> aber **NICHT geforkt, NICHT geklont**: eine saubere Clean-Room-Reimplementierung,
> die wir vollständig eigenständig lizenzieren können.
> **Build in Public.**

---

## 0. Oberste Direktiven (nicht verhandelbar)

1. **Plane ist die einzige Source of Truth.** Jede Arbeit — egal wie klein — braucht
   ZUERST einen Task in Plane. Alles, was zu einer Arbeit gehört (Probleme, Lösungen,
   Findings, Evaluationen, Entscheidungen, offene Fragen), wird **in diesem Task**
   festgehalten, nicht nur im Chat. Kein Task = keine Arbeit.
2. **Alle Agenten arbeiten ausschließlich in diesem System.** Jeder Subagent bekommt
   einen Plane-Task-Bezug; seine Ergebnisse landen gebündelt im zugehörigen Task.
3. **Rückfragen ausschließlich über Plane und graphify.** Inhaltliche Projekt-Rückfragen
   werden als Plane-Item (Task/Kommentar) dokumentiert; `graphify` dient als Überblick
   über den gesamten Projektstand.
4. **Komplett & ausschließlich mit dem Plugin „agent-skills" arbeiten.** Das ist das
   verbindliche Toolset für die gesamte Engineering-Arbeit. Bau-Rhythmus über die
   agent-skills-Skills: **spec → plan → build → test → ship** (bzw. spec-driven /
   incremental-implementation). Kein Ad-hoc-Drauflos-Coden außerhalb dieses Plugins.
5. **Clean-Room-Lizenzhygiene.** odysseus ist AGPL-3.0. Wir dürfen es als Referenz
   *lesen*, aber **niemals Code daraus kopieren/übernehmen**. Implementierung erfolgt
   eigenständig aus Spezifikation/Verhalten. Ziel: vollständig freie Lizenzwahl für uns.
6. **Build in Public ⇒ keine Secrets im Repo.** API-Keys, Tokens, Credentials gehören
   NIE in versionierte Dateien (inkl. dieser Datei). Nur über `.env` / Umgebung.
7. **Planung VOR Erstellung — keine Plane-Items ohne Freigabe.** Tasks, Meilensteine
   und Module werden in Plane ERST angelegt, wenn Oliver es ausdrücklich freigibt.
   Während der Planungsphase wird NICHTS angelegt — erst fertig planen, dann auf
   ausdrückliche Nachfrage erstellen.
8. **Dokumentation mit Starlight, zu JEDEM Task.** Doku lebt in `docs-site/` (Astro
   Starlight) und wird beim Erledigen eines Tasks direkt mitgeschrieben — nie nachgelagert.
9. **GitHub von Tag 1, public.** Repo `oliverhees/lokyy-workspace` (Account: oliverhees).
   Alle Commits dort festhalten (Build in Public). VOR jedem Push den Secret-Scan aus
   `SECURITY.md` ausführen — niemals Secrets pushen.

---

## 1. Plane — Zugang & Nutzung

- **Workspace-Slug:** `codelabs`
- **Base URL:** `https://plane.hr-applab.de`
- **Projekt:** `Lokyy Workspace` — Identifier **`LWS`** — Projekt-ID `d15343e0-e704-4f62-bc3c-1d3c975222a0`
- **API-Key:** liegt in `~/.claude.json` unter `mcpServers.plane.env.PLANE_API_KEY` — **niemals** hier oder im Repo notieren.

**Status MCP:** Der Plane-MCP-Server ist **aktiv & verifiziert** (`get_me`, `retrieve_project`,
`list_modules` ok). Plane wird **primär über die MCP-Tools** (`mcp__plane__*`) bedient.
Die REST-API per curl bleibt nur Fallback. (Hinweis: `count_work_items` liefert teils 404 —
stattdessen `list_modules`/`list_work_items` nutzen.)

**REST-Endpoints (v1):**
```
GET    /api/v1/workspaces/codelabs/projects/
POST   /api/v1/workspaces/codelabs/projects/{project_id}/issues/
GET    /api/v1/workspaces/codelabs/projects/{project_id}/issues/
PATCH  /api/v1/workspaces/codelabs/projects/{project_id}/issues/{issue_id}/
POST   /api/v1/workspaces/codelabs/projects/{project_id}/issues/{issue_id}/comments/
GET    /api/v1/workspaces/codelabs/projects/{project_id}/states/
GET    /api/v1/workspaces/codelabs/projects/{project_id}/members/
# Module = Meilensteine:
GET/POST /api/v1/workspaces/codelabs/projects/{project_id}/modules/
```

---

### Plane voll ausschöpfen (volle Power nutzen)

Plane ist unser PM-Tool — wir nutzen die **volle Bandbreite**, nicht nur Tasks. Immer über die `mcp__plane__*`-Tools:

- **Work Items** = Tasks · **Modules** = Meilensteine.
- **Pages** = Projekt-Wiki / Entscheidungs-Log / Status (PM-nahe Doku in Plane; Produkt-Doku bleibt Starlight, Spezifikation in `docs/`). *Hinweis: Pages aktuell NICHT über API/MCP erreichbar (404) — bei Bedarf manuell in der Plane-UI anlegen.*
- **Labels** = Kategorisierung (`backend`, `frontend`, `infra`, `docs`, `security`, `agent`, `sync` …).
- **Priority** + **Relations/Dependencies** = Reihenfolge & Abhängigkeiten sichtbar machen.
- **Cycles** = Sprints (optional). **Worklogs** = Zeiterfassung. **Comments** = Findings/Entscheidungen je Task (Pflicht).

---

## 2. Arbeitsweise (Workflow je Aufgabe)

1. **Task anlegen** in Plane (LWS) — klare Zielbeschreibung.
2. Task auf **in_progress** setzen.
3. Arbeit ausführen (ggf. mit Subagenten — alle mit Task-Bezug).
4. **Findings/Entscheidungen als Kommentar(e)** in den Task schreiben.
5. Task auf **done** setzen, sobald verifiziert.
6. Offene Fragen → eigenes Plane-Item, **nicht** nur im Chat.

---

## 3. Subagenten & Rate-Limit-Vermeidung (verbindlich)

Auslöser-Erfahrung: 5 Subagenten gleichzeitig parallel zu starten löste ein
temporäres Server-Rate-Limit aus („Server is temporarily limiting requests") und
alle Agenten brachen mit 0 Output ab. Daraus die Regeln:

1. **Parallel arbeiten, wo möglich — aber gedeckelt.** Parallelität ist
   ausdrücklich erwünscht und der Default für unabhängige Arbeit. Obergrenze:
   **max. 2–3 Subagenten gleichzeitig**. Größere Fan-outs in **Wellen** staffeln
   (z. B. 3 starten, abwarten, nächste 3), nie ≥4 gleichzeitig im selben Schwung.
   Unabhängige Tool-Calls (Bash/Read/curl) dürfen weiterhin frei im selben Block
   parallel laufen — das Limit gilt für Subagenten-Inferenz, nicht für normale Tools.
2. **Rate-Limit-Fehler NICHT blind wiederholen.** Bei „temporarily limiting
   requests": kurz pausieren, dann gestaffelt/sequenziell erneut — niemals sofort
   denselben parallelen Schwung neu auslösen.
3. **Eigene gezielte Analyse als Ergänzung, nicht Ersatz.** Kleine/punktuelle
   Aufgaben direkt per Grep/Read lösen; für breite Arbeit weiterhin parallele
   Subagenten nutzen — nur innerhalb der Obergrenze aus Regel 1.
4. **Jeder Subagent dicht & begrenzt briefen** (klares Output-Limit, klarer Scope),
   damit Last und Kontext kontrolliert bleiben.
5. **Bei großen Aufgaben sequenziell + zwischenspeichern**: Teilergebnisse sofort
   in den Plane-Task schreiben, damit ein Abbruch keine Arbeit vernichtet.

---

## 4. Referenz-Material

- odysseus-Klon (read-only Referenz, NICHT Teil unseres Repos):
  `<scratchpad>/odysseus-ref/` — nur zum Lesen/Verstehen, nie kopieren.

---

## 5. Getroffene Entscheidungen & Anforderungen (Planungsphase, in Arbeit)

**Bestätigt:**
- **Architektur:** Hybrid — **Frontend TypeScript** (Next.js, als PWA), **Backend Python/FastAPI**.
- **Datenbank:** **PostgreSQL** (über SQLAlchemy/SQLModel als ORM; pgvector statt separatem ChromaDB prüfen).
- **MVP:** schmaler Killer-Kern zuerst (Chat + Agents + Tools + 1–2 Differenzierungs-Features).
- **Zielgruppe:** Selbstständige & KMU (Telos M0/G0).
- **Deployment:** nur self-hosted (Docker); SaaS evtl. später.
- **DE-Differenzierung:** verbindlich (DSGVO-by-default, EU-Hosting, deutsche Provider, eIDAS-Signatur, DE-Lokalisierung).

**Große Anforderungen (noch zu designen, NICHT als Tasks anlegen):**
- **Kontext-/Lern-Layer:** Telos (Daniel Miessler) + `Soul.md`/`User.md` im Workspace; selbst­verbessernder Agent (lernt Nutzer über Zeit kennen).
- **Memory** (Konzept von odysseus übernehmen, mit pgvector integrieren).
- **Multi-Agent / Orchestrator** (Orchestrator callt & parallelisiert Sub-Agenten).
- **Workflows & Skill-Verkettung** (Schritt-Ketten, zeitgesteuert, vollautomatisch, mit Ergebnis-Artefakten + Notifications).
- **Lokal ↔ Server-Umschaltung + Synchronisation** (Workspace-Sync, Offline/PWA, geteilte Mitarbeiter-Workspaces) — das komplexeste Teilprojekt.
- **Lizenzmodell:** eigene freie Lizenz (nicht AGPL) — final festlegen.

---

## 6. Engineering-Standards

- **Pydantic v2 voll ausschöpfen:** `pydantic-settings` für Config (`.env` → typisierte Settings,
  kein rohes `os.getenv`); **SQLModel** (Pydantic+SQLAlchemy) für DB-Modelle; Pydantic-Schemas für
  ALLE API-Requests/Responses; **strikte Validierung** (Input-Hygiene = Sicherheit/DSGVO);
  `field_validator`/`model_validator` & `computed_field` wo sinnvoll; Pydantic für **strukturierte
  LLM-Outputs** (Tool-Calls/Agent-Antworten validieren statt roh parsen).
- **bun/bunx** im Frontend (kein npm/npx), **TypeScript** durchgängig.
- **Test-driven** wo sinnvoll (RED→GREEN), grüner Build vor jedem Commit.
- **Doku (Starlight) zu jedem Task** — siehe Direktive 8.

---

## 7. Lokale Dev-Umgebung (Ports & bestehende Dienste)

Auf dem Dev-Rechner laufen bereits andere Lokyy-/Infra-Container (lokyy-brain, lokyy-os,
hermes, traefik …). Belegt u. a.: **80, 443, 5432, 5433, 8000, 8001**.

- **Unser Stack:** Backend-Host-Port **8008** (Default, via `APP_PORT` konfigurierbar);
  PostgreSQL ist **intern-only** (kein Host-Mapping → kein Konflikt, sicherer).
- **Vor jedem Docker-Test freie Ports prüfen** (`ss -tlnH "( sport = :PORT )"`) und den Stack
  danach mit `docker compose down` stoppen.
- **Health-Verifikation immer schema-genau** (`/health` muss `version` enthalten) — sonst droht
  ein False Positive durch einen fremden Dienst auf demselben Port (genau das ist bei T0.2 passiert).
