---
title: Systemarchitektur (Stand M0)
description: Wie Lokyy Workspace nach dem Fundament-Meilenstein konkret gebaut ist.
---

Dieser Überblick beschreibt den **tatsächlichen Code-Stand nach M0** (nicht die Vision —
die liegt in `docs/KONZEPT.md`).

## Überblick

```
Frontend (Next.js 16, PWA)  ──HTTP──>  Backend (FastAPI)  ──>  PostgreSQL + pgvector
   konfigurierbare Backend-URL              owner/org-scoped
   (Lokal / Remote Switch)                  Auth (Sessions/2FA/Tokens)
```

## Backend (`backend/`)

- **`app/main.py`** — FastAPI-Entrypoint, registriert Router (`/health`, `/`, `/auth/*`).
- **`app/core/`**
  - `config.py` — getypte Settings via **pydantic-settings** (kein rohes `os.getenv`).
  - `db.py` — SQLModel-Engine + Session-Dependency.
  - `security.py` — argon2id-Passwörter, SHA-256 API-Token-Hashing.
  - `auth.py` — Registrierung, Login, Server-Sessions, TOTP-2FA + Backup-Codes, API-Tokens.
  - `scoping.py` — **Multi-Tenant-Guard** (`scope_to_org`, `scope_to_owner`).
- **`app/models/`** — SQLModel-Entitäten: Organization, User, Workspace, Membership,
  ChatSession, ChatMessage (`entities.py`) + AuthSession, ApiToken, BackupCode (`auth.py`).
  Durchgängig `organization_id`/`owner_id`, FK-CASCADE.
- **`app/api/`** — `auth_routes.py` (HTTP) + `deps.py` (`get_current_user`: Bearer-Token **oder** Session-Cookie).
- **`alembic/`** — Migrationen, an SQLModel-Metadaten gebunden.
- **Tests:** `tests/` (pytest, 18+ — Security, Service, Endpoints, Scoping-Isolation).

### Auth-Flow
Registrieren → Login (prüft Passwort, erzwingt 2FA wenn aktiv) → Server-Session (httponly-Cookie)
oder API-Token (Bearer). Jeder Request wird über `get_current_user` aufgelöst. Secrets nur als Hash.

### Multi-Tenancy
Jede mandantenbezogene Query MUSS durch `app/core/scoping.py`. Org-Admins sehen ihre ganze Org,
andere nur Eigenes. Geteilte Workspaces (Membership) folgen in M7. (Defense-in-Depth: Postgres RLS später — siehe ADR-0001.)

## Frontend (`frontend/`)

- **Next.js 16** (App Router, **bun**), **Tailwind v4** mit Brand-Theme (Cyan→Blau, `app/globals.css`).
- **`lib/connection.ts`** — Verbindungs-Layer: Lokal/Remote, konfigurierbare Backend-URL, localStorage.
- **`lib/api.ts`** — API-Client + Health-Check.
- **`components/ConnectionSwitch.tsx`** — Lokal/Remote-Umschalter mit Live-Status.
- **i18n** (next-intl): `messages/de.json` (default) + `en.json`, Cookie-basiert, `LanguageSwitch`. Keine hardcoded Strings.
- **PWA:** `public/manifest.webmanifest`.

## Infrastruktur

- **Docker Compose** (`docker-compose.yml`): Backend + `pgvector/pgvector:pg17` (DB **intern-only**).
  Backend-Host-Port konfigurierbar (Default 8008), siehe CLAUDE.md §7.
- **CI** (`.github/workflows/ci.yml`): Backend-pytest · Frontend-Build · Secret-Scan.

## Doku-Landkarte

- `docs/KONZEPT.md` — vollständige Architektur-Vision · `docs/PROJEKTBESCHREIBUNG.md` — Produktbeschreibung
- `docs/UMSETZUNGSPLAN.md` — Meilensteine/Tasks · `docs/mockups/` — UI-Mockups
- ADR-0001 — DB-Entscheidungen · diese Seite — realer Stand
- Plane (`LWS`) — Single Source of Truth für Tasks/Fortschritt
