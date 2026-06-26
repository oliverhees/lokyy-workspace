"""Lokyy Workspace — FastAPI application entrypoint.

M0/T0.2: minimal runnable app with a health endpoint. DB models, auth and
feature routers land in the following M0 tasks.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.auth_routes import router as auth_router
from app.api.chat_routes import router as chat_router
from app.api.context_routes import router as context_router
from app.api.model_routes import router as model_router
from app.api.project_routes import router as project_router
from app.api.session_routes import router as session_router
from app.api.settings_routes import router as settings_router
from app.core.config import get_settings

settings = get_settings()

# Fail fast on insecure configuration (weak secret / cookies / wildcard CORS).
_issues = settings.security_issues()
if _issues:
    raise RuntimeError("Unsichere Konfiguration: " + " ".join(_issues))

app = FastAPI(
    title="Lokyy Workspace API",
    version="0.0.1",
    description="The self-hosted AI operating system for the self-employed and SMEs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(settings_router)
app.include_router(model_router)
app.include_router(session_router)
app.include_router(context_router)
app.include_router(project_router)


class HealthResponse(BaseModel):
    """Typed health payload (Pydantic response schema)."""

    status: str
    env: str
    version: str


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", env=settings.app_env, version=app.version)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"name": "Lokyy Workspace API", "docs": "/docs"}
