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
- **F3 — Settings-Framework** ⏳
  Zentrale Einstellungen (Backend-Persistenz + Settings-Seite: Profil, Sprache/Theme,
  Verbindung lokal/server). Erweiterbar.
- **F4 — Modell-Verwaltung (modell-agnostisch)** ⏳
  `ModelEndpoint` (base_url, model, **api_key verschlüsselt**) + CRUD-API; Settings-Sektion.
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
| Einstellungen   | „bald"           | **F3** (Settings-Framework) |

**Startseite:** Aktuell ist die öffentliche `app/page.tsx` die Marketing-Landing
(für Nicht-Eingeloggte), nach Login wird auf `/chat` geleitet. Im Mockup ist die
Startseite nach Login das **Dashboard** („Guten Morgen, …", Stat-Karten, Quick-Actions,
Übersicht über Workflows/Projekte/Lernen). Das Dashboard zeigt Daten aus mehreren noch
nicht gebauten Features — daher als **eigener Folge-Task** vorgesehen (Grundgerüst mit
Platzhaltern früh möglich, echte Daten sobald die Features existieren). _Noch nicht in
Plane angelegt — Freigabe ausstehend._

## Notizen

- **Lokale DB:** Dev läuft jetzt (seit F1.1) gegen eine **dedizierte Docker-Dev-Postgres**
  auf Host-Port 5435 (`docker-compose.dev.yml`). Die Produktiv-DB bleibt internal-only.
  Ports 5432–5434 sind auf der Dev-Maschine durch andere Infra belegt — daher 5435.
- **Unit-Tests** laufen weiterhin gegen In-Memory-SQLite (schnell, ohne DB-Abhängigkeit);
  der produktionsnahe Postgres-Pfad ist durch die Alembic-Migrationen + die E2E-Verifizierung
  abgedeckt.
