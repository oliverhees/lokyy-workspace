"""Model endpoint HTTP routes (F4): owner-scoped CRUD, keys encrypted at rest.

Responses expose `has_api_key` (bool) only — the plaintext key is never returned.
The current user comes from the auth dependency, so every operation is owner-scoped.
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import model_service, ssrf
from app.core.config import get_settings
from app.core.db import get_session
from app.core.llm import KNOWN_PROVIDERS
from app.models.entities import ModelEndpoint, User


def _check_provider(v: str | None) -> str | None:
    if v is not None and v not in KNOWN_PROVIDERS:
        raise ValueError(f"unknown provider: {v}")
    return v

router = APIRouter(prefix="/models", tags=["models"])


class ModelOut(BaseModel):
    id: str
    name: str
    provider: str
    base_url: str
    model: str
    is_default: bool
    has_api_key: bool


class ModelCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    provider: str = "openai"
    base_url: str = ""  # optional: native providers (Anthropic, Gemini) use LiteLLM defaults
    model: str = Field(min_length=1)
    api_key: str = ""
    is_default: bool = False

    @field_validator("provider")
    @classmethod
    def _check(cls, v: str) -> str:
        return _check_provider(v)  # type: ignore[return-value]


class ModelUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    provider: str | None = None
    base_url: str | None = None
    model: str | None = None
    api_key: str | None = None  # null = unchanged, "" = clear

    @field_validator("provider")
    @classmethod
    def _check(cls, v: str | None) -> str | None:
        return _check_provider(v)


class DiscoverIn(BaseModel):
    provider: str
    base_url: str = ""
    api_key: str = ""

    @field_validator("provider")
    @classmethod
    def _check(cls, v: str) -> str:
        return _check_provider(v)  # type: ignore[return-value]


class DiscoverOut(BaseModel):
    models: list[str]


def _out(ep: ModelEndpoint) -> ModelOut:
    return ModelOut(
        id=ep.id, name=ep.name, provider=ep.provider, base_url=ep.base_url,
        model=ep.model, is_default=ep.is_default, has_api_key=bool(ep.api_key_encrypted),
    )


@router.get("", response_model=list[ModelOut])
def list_models(db: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list[ModelOut]:
    return [_out(e) for e in model_service.list_endpoints(db, user_id=user.id)]


@router.post("/discover", response_model=DiscoverOut)
async def discover_models(body: DiscoverIn, user: User = Depends(get_current_user)) -> DiscoverOut:
    """Fetch the provider's available model ids via its OpenAI-compatible /models endpoint.

    The key is used only for this call and never stored. Needs a base_url (native
    providers without one fall back to manual entry).
    """
    base = body.base_url.strip()
    if not base:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Für diesen Anbieter ist keine automatische Modell-Liste verfügbar — "
            "bitte die Modell-ID manuell eingeben.",
        )
    try:
        ssrf.validate_outbound_url(base, allow_private=get_settings().allow_private_model_hosts)
    except ssrf.UnsafeUrlError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Base-URL nicht erlaubt: {e}")
    url = base.rstrip("/") + "/models"
    headers = {"Authorization": f"Bearer {body.api_key}"} if body.api_key else {}
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Anbieter antwortete mit {e.response.status_code} — API-Key prüfen?",
        )
    except Exception:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Modelle konnten nicht geladen werden — Base-URL/Verbindung prüfen.",
        )
    items = data.get("data") if isinstance(data, dict) else data
    ids = sorted({
        m["id"] for m in (items or []) if isinstance(m, dict) and isinstance(m.get("id"), str)
    })
    return DiscoverOut(models=ids)


@router.post("", response_model=ModelOut, status_code=status.HTTP_201_CREATED)
def create_model(body: ModelCreateIn, db: Session = Depends(get_session),
                 user: User = Depends(get_current_user)) -> ModelOut:
    try:
        ep = model_service.create_endpoint(
            db, user_id=user.id, name=body.name, provider=body.provider,
            base_url=body.base_url, model=body.model, api_key=body.api_key,
            is_default=body.is_default,
        )
    except model_service.ModelError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return _out(ep)


@router.put("/{endpoint_id}", response_model=ModelOut)
def update_model(endpoint_id: str, body: ModelUpdateIn, db: Session = Depends(get_session),
                 user: User = Depends(get_current_user)) -> ModelOut:
    try:
        ep = model_service.update_endpoint(
            db, user_id=user.id, endpoint_id=endpoint_id, name=body.name,
            provider=body.provider, base_url=body.base_url, model=body.model,
            api_key=body.api_key,
        )
    except model_service.ModelError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    return _out(ep)


@router.post("/{endpoint_id}/default", response_model=ModelOut)
def set_default_model(endpoint_id: str, db: Session = Depends(get_session),
                      user: User = Depends(get_current_user)) -> ModelOut:
    try:
        ep = model_service.set_default(db, user_id=user.id, endpoint_id=endpoint_id)
    except model_service.ModelError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    return _out(ep)


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(endpoint_id: str, db: Session = Depends(get_session),
                 user: User = Depends(get_current_user)) -> None:
    try:
        model_service.delete_endpoint(db, user_id=user.id, endpoint_id=endpoint_id)
    except model_service.ModelError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
