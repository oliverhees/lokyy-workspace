# Lokyy Workspace — Backend

Python · FastAPI · SQLModel · PostgreSQL + pgvector · Alembic.

## Status (M0)

- ✅ FastAPI app (`/health`, `/`) — typed config via **pydantic-settings**
- ✅ Multi-tenant data model (Organization, User, Workspace, Membership, ChatSession, ChatMessage) with owner/org scoping
- ✅ Auth: argon2 passwords, server-side sessions, TOTP 2FA + backup codes, hashed API tokens
- ✅ Alembic migrations (verified against Postgres)

## Layout

```
backend/
├── app/
│   ├── main.py            # FastAPI entrypoint + router registration
│   ├── core/              # config, db, security, auth, scoping
│   ├── models/            # SQLModel entities + auth tables
│   └── api/               # routers (auth_routes) + deps
├── alembic/               # migrations (env wired to SQLModel metadata)
└── tests/                 # pytest (18+ tests)
```

## Develop

```bash
# via Docker (recommended — see repo root):
docker compose up -d --build           # backend on http://localhost:8008

# or locally:
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest              # run tests
.venv/bin/uvicorn app.main:app --reload --port 8008
```

Migrations: `alembic upgrade head` (DB URL from `DATABASE_URL`).
