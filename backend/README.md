# Lokyy Workspace — Backend

Python · FastAPI · SQLAlchemy/SQLModel · PostgreSQL + pgvector.

> 🚧 Placeholder structure (M0/T0.1). The runnable FastAPI app, DB foundation and auth
> land in the following M0 tasks (T0.2–T0.4). See [`../ROADMAP.md`](../ROADMAP.md).

## Planned layout

```
backend/
├── app/            # FastAPI application
│   ├── main.py     # app entrypoint (T0.2)
│   ├── core/       # config, db, auth, security
│   ├── models/     # SQLAlchemy/SQLModel (T0.3)
│   └── api/        # routers
└── tests/          # pytest
```
