---
title: ADR-0001 — Datenbank-Fundament & Multi-Tenant-Scoping
description: Architekturentscheidungen für das DB-Fundament (T0.3).
---

**Status:** akzeptiert · **Kontext:** M0/T0.3

## Entscheidung

- **ORM: SQLModel** (Pydantic + SQLAlchemy) auf **PostgreSQL** — eine Typebene für DB-Modelle und API-Schemas (Pydantic voll ausschöpfen). Zunächst **synchron** (einfacher, gut testbar); ein späterer Wechsel auf async bleibt möglich.
- **Migrationen: Alembic**, `env.py` an `SQLModel.metadata` gebunden, DB-URL aus den getypten Settings (kein Hardcoding). Migrations-Template um `import sqlmodel` ergänzt.
- **Multi-Tenancy:** jede mandantenbezogene Zeile trägt `organization_id`; nutzereigene Zeilen zusätzlich `owner_id`. Zugriff ausschließlich über die Helfer in `app/core/scoping.py` (`scope_to_org`, `scope_to_owner`).
- **Geteilte Workspaces** über `Membership` (Rolle owner/member/viewer) — der membership-basierte Lesezugriff wird mit **M7 (Sync & Team)** in das Scoping integriert.

## Konsequenzen & bekannte Risiken

- **Scoping ist opt-in** → eine vergessene rohe Query kann Tenant-Grenzen überschreiten. Gegenmaßnahme: Disziplin + Tests; als Defense-in-Depth ist **PostgreSQL Row-Level-Security** für später vorgemerkt.
- **FK-`CASCADE`** hält die Hierarchie sauber (Org → User/Workspace → Session → Message), löscht aber kaskadierend — bei destruktiven Operationen beachten.
- `email` ist aktuell global eindeutig (nicht pro Org) — für späteren Multi-Tenant-SaaS zu überdenken.
