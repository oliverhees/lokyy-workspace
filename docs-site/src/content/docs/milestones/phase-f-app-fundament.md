---
title: Phase F — App-Fundament & Shell
description: Tragende Anwendung zuerst — Login, Shell, Settings, Modell, echter Chat.
sidebar:
  order: 2
---

**Ziel:** die nutzbare Anwendung *vor* den Feature-Meilensteinen. Erst das Fundament
(Login → App-Shell → Settings → echte Modell-Anbindung → Chat mit Verlauf), dann die
Features (M2 ff.). Vertikale Durchstiche statt horizontaler Layer.

> Warum diese Phase: M0/M1 lieferten die *Bausteine* (Auth-Backend, LLM-Layer,
> Agent-Loop, Tools, Chat-UI), aber keine zusammenhängende App, die sie nutzbar macht.
> Phase F schließt diese Lücke.

## Tasks

- **F1 — Auth end-to-end (Login/Registrierung/2FA/Logout-UI)** ✅
  Frontend gegen das bestehende Auth-Backend. Neuer Backend-Endpoint `POST /auth/signup`
  (Self-Hosting-Bootstrap: legt Organisation + ersten Nutzer als Org-Admin an und loggt
  direkt ein). Frontend: `lib/auth.ts` (API-Client, httpOnly-Session-Cookie),
  `AuthProvider` (lädt `/auth/me` beim Start → eingeloggt bleiben), `RequireAuth`
  (geschützte Routen), Login/Registrierungs-Seite (`/login`) mit 2FA-Schritt im
  Brand-Design (DE/EN), `UserMenu` (Name + Abmelden). Chat-Seite hinter `RequireAuth`.
  **Verifiziert (Chrome, SQLite-Dev-DB):** Registrierung → Auto-Login → `/chat`,
  Reload bleibt eingeloggt, Logout → `/login`, `/chat` ausgeloggt → Redirect auf
  `/login`, Login mit Bestandskonto → `/chat`. Backend +1 Test (49 grün). Konsole sauber.
- **F1.1 — Dedizierte Dev-Postgres (Docker)** ✅
  Folge-Task aus F1: eigene Dev-Postgres statt der belegten Fremd-Infra. Die Produktiv-DB
  bleibt **internal-only**; ein explizites Dev-Override (`docker-compose.dev.yml`) mappt die
  DB auf den freien Host-Port **5435**, damit das Host-Backend (Hot-Reload) sie erreicht.
  Lokale `.env` (gitignored) mit `DATABASE_URL`, Schema via **Alembic-Migrationen**
  (`alembic upgrade head`, nicht `init_db`). **Verifiziert:** Signup/Login E2E grün gegen
  echtes Postgres (Daten in `users`/`organizations` geprüft), UI-Login bestätigt.
  Start: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db`.
- **F2 — App-Shell + Navigation** ✅
  Authentifizierte Layout-Hülle über die Route-Gruppe `app/(app)/` (URL bleibt unverändert):
  `(app)/layout.tsx` umschließt alle Feature-Seiten mit `RequireAuth` + persistenter
  **Sidebar** (`components/shell/Sidebar.tsx`: Logo, Nav mit Aktiv-Highlight via
  `usePathname`; Chat aktiv, Dashboard/Einstellungen als „bald" disabled — sichtbare
  Produktform ohne Dead-Links) und **Topbar** (`components/shell/Topbar.tsx`: Seitentitel
  aus dem Pfad, Connection-Switch, Sprache, `UserMenu`). Chat von `app/chat/` nach
  `app/(app)/chat/` migriert, eigener Header entfernt (kommt jetzt aus der Shell).
  Nav-Labels i18n (DE/EN). **Verifiziert (Chrome):** Shell rendert, Chat-Highlight aktiv,
  „bald"-Items sind keine Links, Logout aus der Topbar → `/login`. Build + Konsole sauber.
- **F3 — Settings-Framework** ✅
  Zentrale Einstellungen, über die alles läuft. **Backend:** `UserSettings` (owner-scoped,
  1 Zeile/User, get-or-create) + Migration + API `GET/PUT /settings` & `PUT /settings/profile`,
  strikt validiert (Pydantic `Literal`). **Frontend:** Settings-Seite (`/settings`) mit
  Sektionen Profil (Name editierbar, E-Mail readonly), Darstellung (Sprache, Theme) und
  Verbindung (Standard lokal/server); erweiterbar (F4 hängt „Modelle" hier ein). Sidebar-Punkt
  „Einstellungen" scharf geschaltet. Server-side Source-of-Truth, Client spiegelt
  Theme/Verbindung in `localStorage` für sofortige Anwendung. **Theme:** echtes class-based
  Dark/Light via `@custom-variant dark` + Anti-FOUC-Script (Tailwind v4 nutzt sonst nur
  `prefers-color-scheme`). **Verifiziert:** 8 Backend-Tests (CRUD, Validierung,
  Owner-Isolation, Auth-Enforcement → 57 gesamt), Sichtprüfung (Theme Dunkel↔Hell schaltet
  sofort + persistiert in Postgres), Konsole sauber.
- **F3.1 — Settings-UI-Politur** ✅
  Sektionen über eine **Tab-Navigation** innerhalb der Seite (Profil · Darstellung ·
  Verbindung) statt gestapelt; der Modelle-Tab (F4) hängt sich hier ein. Buttons global
  etwas kompakter (geringere Höhe). Verifiziert (Chrome): Tab-Wechsel, Brand, Konsole sauber.
- **F4 — Modell-Verwaltung (modell-agnostisch)** ✅
  `ModelEndpoint` (name, provider, base_url, model, **api_key verschlüsselt at rest**) + Migration,
  owner-scoped CRUD-API (`/models`, GET/POST/PUT/DELETE + `/{id}/default`). Verschlüsselung via
  `app/core/crypto.py` (Fernet, Key aus `SECRET_KEY` abgeleitet); der Klartext-Key wird **nie**
  zurückgegeben (Response nur `has_api_key`). Default-Handling (erstes Modell wird Default,
  Umschalten räumt andere auf, Löschen befördert nächstes). **Frontend:** „Modelle"-Tab in den
  Settings (`components/settings/ModelsTab.tsx`) — Liste mit Default-/Key-Badges, Anlegen/Bearbeiten
  (Key-Feld write-only) /Löschen/Als-Standard, i18n DE/EN. **Verifiziert:** 10 Backend-Tests
  (CRUD, Crypto-Roundtrip, Default-Logik, Owner-Isolation, Key-nie-im-Klartext → 67 gesamt),
  Sichtprüfung (Modell anlegen → Liste, Badges) + **DB-Check: Key liegt als Fernet-Token vor,
  kein Klartext**. Konsole sauber.
- **F4.1 — LLM-Layer auf LiteLLM (Multi-Provider)** ✅
  Eigener httpx-LLM-Layer durch **LiteLLM** ersetzt (`app/core/llm.py`) — eine API + ein
  Response-Format für 100+ Provider. Routing: `"<provider>/<model>"`, `custom` → OpenAI-kompatibel
  via `api_base` (deckt selbst gehostete / OpenAI-API-Standard-Endpoints ab). `chat()`/`stream_chat()`
  behalten ihre Form → **Agent-Loop und Chat-Route unverändert** (Agent-Loop war eh über einen
  injizierten Caller entkoppelt). Provider-Liste zentral (`KNOWN_PROVIDERS`), von Modell-Service +
  Routes genutzt. **Frontend:** Anbieter-Presets (`lib/providers.ts`) im Modelle-Tab — OpenRouter
  prominent („alle großen Modelle"), OpenAI, Anthropic, Gemini, Groq, Mistral, DeepSeek, Together,
  Ollama lokal, **Eigene/OpenAI-kompatibel**; Provider-Wahl füllt die Base-URL automatisch.
  **Verifiziert:** Backend-Suite grün (69, LLM-Tests auf LiteLLM-Mock umgestellt), Sichtprüfung
  (10 Provider, OpenRouter-Default, Base-URL-Autofill bei Ollama), Konsole sauber.
- **F5 — Chat echt + Sessions + Sidebar** ⏳
  `/chat` nutzt den echten Agent-Loop gegen das konfigurierte Modell; Sessions persistieren;
  Sidebar mit Konversationsliste. **🚩 Checkpoint + QA-Gate** danach, dann M2 ff.

## Sidebar-Zielbild & Startseite (aus dem Mockup)

Das Dashboard-Mockup (`docs/mockups/lokyy-dashboard-*.png`) zeigt die Vollausbau-Vision.
Die in F2 gebaute Shell ist bewusst die **Grundstruktur**; sie wächst **inkrementell mit
den Features** — jeder Sidebar-Punkt wird aktiviert, wenn sein Feature existiert (keine
Dead-Links, daher aktuell „bald"-Markierung).

**Sidebar-Punkte (Mockup) → Feature/Task, der sie aktiviert:**

| Sidebar-Punkt   | Status F2        | Aktiviert durch        |
|-----------------|------------------|------------------------|
| Dashboard       | „bald"           | Startseite-Task (s. u.)|
| Chats           | ✅ aktiv          | F1/F2                  |
| Projekte        | _noch nicht_     | M3 (Projekte/Editor)   |
| Workflows       | _noch nicht_     | M4 (Workflows/Multi-Agent) |
| Dateien         | _noch nicht_     | M3                     |
| Skills          | _noch nicht_     | M4                     |
| Team            | _noch nicht_     | M7 (Sync/Team)         |
| Einstellungen   | ✅ aktiv          | **F3** (Settings-Framework) |

**Startseite:** Aktuell ist die öffentliche `app/page.tsx` die Marketing-Landing
(für Nicht-Eingeloggte), nach Login wird auf `/chat` geleitet. Im Mockup ist die
Startseite nach Login das **Dashboard** („Guten Morgen, …", Stat-Karten, Quick-Actions,
Übersicht über Workflows/Projekte/Lernen). Das Dashboard zeigt Daten aus mehreren noch
nicht gebauten Features.

**Entscheidung (Oliver):** beim Plan bleiben — erst **F3 → F5** (Settings, Modell, echter
Chat), das **Dashboard danach als eigener Task**, damit es echte Daten anzeigt statt leerer
Platzhalter. Bis dahin bleibt nach Login `/chat` die Startseite. _Dashboard-Task wird bei
Freigabe nach F5 angelegt._

## Notizen

- **Lokale DB:** Dev läuft jetzt (seit F1.1) gegen eine **dedizierte Docker-Dev-Postgres**
  auf Host-Port 5435 (`docker-compose.dev.yml`). Die Produktiv-DB bleibt internal-only.
  Ports 5432–5434 sind auf der Dev-Maschine durch andere Infra belegt — daher 5435.
- **Unit-Tests** laufen weiterhin gegen In-Memory-SQLite (schnell, ohne DB-Abhängigkeit);
  der produktionsnahe Postgres-Pfad ist durch die Alembic-Migrationen + die E2E-Verifizierung
  abgedeckt.
