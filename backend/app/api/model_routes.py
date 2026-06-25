"""Model endpoint HTTP routes (F4): owner-scoped CRUD, keys encrypted at rest.

Responses expose `has_api_key` (bool) only — the plaintext key is never returned.
The current user comes from the auth dependency, so every operation is owner-scoped.
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import model_service
from app.core.db import get_session
from app.models.entities import ModelEndpoint, User

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
    provider: Literal["openai", "anthropic"] = "openai"
    base_url: str = Field(min_length=1)
    model: str = Field(min_length=1)
    api_key: str = ""
    is_default: bool = False


class ModelUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    provider: Literal["openai", "anthropic"] | None = None
    base_url: str | None = None
    model: str | None = None
    api_key: str | None = None  # null = unchanged, "" = clear


def _out(ep: ModelEndpoint) -> ModelOut:
    return ModelOut(
        id=ep.id, name=ep.name, provider=ep.provider, base_url=ep.base_url,
        model=ep.model, is_default=ep.is_default, has_api_key=bool(ep.api_key_encrypted),
    )


@router.get("", response_model=list[ModelOut])
def list_models(db: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list[ModelOut]:
    return [_out(e) for e in model_service.list_endpoints(db, user_id=user.id)]


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
