---
title: M0 — Fundament & Setup
description: Lauffähiges Skelett, public auf GitHub, von Tag 1.
---

**Ziel:** lauffähiges Skelett (Backend + Frontend + DB + Auth in Docker), **public auf GitHub von Tag 1**, mit sauberer Lizenz- und Secret-Hygiene.

## Tasks

- **T0.1 — Monorepo-Setup + Lizenz (AGPL-3.0 + CLA)** ✅
  Monorepo-Struktur (`backend/`, `frontend/`, `docs-site/`), AGPL-3.0-Lizenz + CLA, zweisprachige README (DE/EN), ROADMAP, SECURITY (Secret-Hygiene + Pre-Push-Scan), CONTRIBUTING, `.gitignore`, `.env.example`, Starlight-Doku-Gerüst, öffentliches GitHub-Repo.
- **T0.2 — Docker Compose: FastAPI + PostgreSQL + pgvector** ✅
  Lauffähiger Container-Stack: FastAPI-Backend (pydantic-settings für getypte Config) mit `/health` + `/`, PostgreSQL+pgvector (`pgvector/pgvector:pg17`, healthcheck, intern-only). pytest grün, End-to-End gegen den echten Stack verifiziert. Host-Ports konfigurierbar (Backend default 8008).
- **T0.3 — DB-Fundament + owner/org-scoping** ✅
  SQLModel-Entitäten (Organization, User, Workspace, Membership, ChatSession, ChatMessage) mit durchgängigem `organization_id`/`owner_id`-Scoping (`app/core/scoping.py`), FK-`CASCADE`, `updated_at`-`onupdate`. Alembic eingerichtet (env.py auf SQLModel-Metadaten) + erste Migration generiert & gegen Postgres verifiziert. 5 Tests grün. Code-Review (5 Achsen) durchgeführt, Findings eingearbeitet. Siehe [ADR-0001](/architecture/adr-0001-datenbank/).
- **T0.4 — Auth: Sessions, 2FA, API-Tokens** ✅
  argon2id-Passwörter, server-seitige (revozierbare) Sessions, TOTP-2FA + Einmal-Backup-Codes, gehashte API-Tokens mit Scopes. HTTP-Endpoints (`/auth/register|login|logout|me|2fa/setup|2fa/enable|tokens`) mit Pydantic-Schemas; Auth-Dependency (Bearer-Token **oder** httponly-Session-Cookie). Alembic-Migration `d5bfeaca19b8`. 18 Tests grün. Secrets nur als Hash gespeichert.
- **T0.5 — Next.js-PWA-Grundgerüst + Verbindungs-Switch** ✅
  Next.js 15 (App Router, bun) + Tailwind v4 mit Brand-Theme (Cyan→Blau), PWA-Manifest. **Verbindungs-Switch** Lokal/Remote (konfigurierbare Backend-URL + Live-Health-Check). **i18n-Grundarchitektur** (next-intl, DE default + EN, Cookie-basiert) — keine hardcoded Strings. Build grün; **Sichtprüfung** mit echtem Chrome bestanden (DE + EN, Brand, Offline-Erkennung).
- **T0.6 — CI + Test-Grundgerüst** ⬜

## Prinzipien

- **Build in Public:** alles offen, keine Secrets im Repo.
- **Clean-Room:** kein Fremdcode aus AGPL-Referenzen (z. B. odysseus).
- **Doku zu jedem Task:** diese Starlight-Doku wächst mit jedem erledigten Task.
