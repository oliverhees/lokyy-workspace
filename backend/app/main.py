"""Lokyy Workspace — FastAPI application entrypoint.

M0/T0.2: minimal runnable app with a health endpoint. DB models, auth and
feature routers land in the following M0 tasks.
"""
from fastapi import FastAPI
from pydantic import BaseModel

from app.api.auth_routes import router as auth_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Lokyy Workspace API",
    version="0.0.1",
    description="The self-hosted AI operating system for the self-employed and SMEs.",
)

app.include_router(auth_router)


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
