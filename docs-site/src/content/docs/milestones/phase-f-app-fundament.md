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
- **F2 — App-Shell + Navigation** ⏳
  Authentifizierte Layout-Hülle: Sidebar (Menüpunkte), Topbar (User-Menü,
  Connection-Switch, Sprache), Routing-Gruppe. Hülle, in die alle Features einhängen.
- **F3 — Settings-Framework** ⏳
  Zentrale Einstellungen (Backend-Persistenz + Settings-Seite: Profil, Sprache/Theme,
  Verbindung lokal/server). Erweiterbar.
- **F4 — Modell-Verwaltung (modell-agnostisch)** ⏳
  `ModelEndpoint` (base_url, model, **api_key verschlüsselt**) + CRUD-API; Settings-Sektion.
- **F5 — Chat echt + Sessions + Sidebar** ⏳
  `/chat` nutzt den echten Agent-Loop gegen das konfigurierte Modell; Sessions persistieren;
  Sidebar mit Konversationsliste. **🚩 Checkpoint + QA-Gate** danach, dann M2 ff.

## Notizen

- **F1-DB beim Verifizieren:** Die E2E-Sichtprüfung lief gegen eine lokale **SQLite-Dev-DB**
  (echtes HTTP, echte DB-Writes, echte Session-Cookies). Der PostgreSQL-Pfad ist durch die
  Alembic-Migrationen und die Unit-Tests abgedeckt. Eine dedizierte Dev-Postgres-Instanz
  (statt der belegten Fremd-Infra auf Port 5432) ist ein eigener, kleiner Folge-Task.
