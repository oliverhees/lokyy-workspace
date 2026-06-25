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
- **T0.3 — DB-Fundament + owner/org-scoping** ⬜
- **T0.4 — Auth: Sessions, 2FA, API-Tokens** ⬜
- **T0.5 — Next.js-PWA-Grundgerüst + Verbindungs-Switch** ⬜
- **T0.6 — CI + Test-Grundgerüst** ⬜

## Prinzipien

- **Build in Public:** alles offen, keine Secrets im Repo.
- **Clean-Room:** kein Fremdcode aus AGPL-Referenzen (z. B. odysseus).
- **Doku zu jedem Task:** diese Starlight-Doku wächst mit jedem erledigten Task.
