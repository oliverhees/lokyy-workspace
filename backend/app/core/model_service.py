"""Model endpoint service (F4): owner-scoped CRUD for model-agnostic LLM endpoints.

API keys are encrypted at rest (app.core.crypto) and never returned in plaintext.
Exactly one endpoint per user can be the default; setting a new default clears the
others. All reads/writes are scoped to user_id — a user can only touch their own.
"""
from sqlmodel import Session, select

from app.core import crypto
from app.core.llm import KNOWN_PROVIDERS
from app.models.entities import ModelEndpoint

# Model-agnostic: any LiteLLM-supported provider, plus "custom" for any
# OpenAI-API-standard endpoint (self-hosted / unlisted). Single source: llm.py.
ALLOWED_PROVIDERS = KNOWN_PROVIDERS


class ModelError(Exception):
    """Raised on invalid input or a missing/foreign endpoint."""


def list_endpoints(db: Session, *, user_id: str) -> list[ModelEndpoint]:
    return list(
        db.exec(
            select(ModelEndpoint)
            .where(ModelEndpoint.user_id == user_id)
            .order_by(ModelEndpoint.created_at)
        ).all()
    )


def _get_owned(db: Session, *, user_id: str, endpoint_id: str) -> ModelEndpoint:
    ep = db.get(ModelEndpoint, endpoint_id)
    if ep is None or ep.user_id != user_id:  # owner check — no cross-tenant access
        raise ModelError("endpoint not found")
    return ep


def _clear_other_defaults(db: Session, *, user_id: str, keep_id: str | None) -> None:
    for other in db.exec(
        select(ModelEndpoint).where(
            ModelEndpoint.user_id == user_id, ModelEndpoint.is_default == True  # noqa: E712
        )
    ).all():
        if other.id != keep_id:
            other.is_default = False
            db.add(other)


def create_endpoint(
    db: Session,
    *,
    user_id: str,
    name: str,
    provider: str,
    base_url: str,
    model: str,
    api_key: str = "",
    is_default: bool = False,
) -> ModelEndpoint:
    if provider not in ALLOWED_PROVIDERS:
        raise ModelError("invalid provider")
    # First endpoint becomes default automatically.
    has_any = bool(list_endpoints(db, user_id=user_id))
    make_default = is_default or not has_any
    if make_default:
        _clear_other_defaults(db, user_id=user_id, keep_id=None)
    ep = ModelEndpoint(
        user_id=user_id,
        name=name.strip(),
        provider=provider,
        base_url=base_url.strip(),
        model=model.strip(),
        api_key_encrypted=crypto.encrypt(api_key),
        is_default=make_default,
    )
    db.add(ep)
    db.commit()
    db.refresh(ep)
    return ep


def update_endpoint(
    db: Session,
    *,
    user_id: str,
    endpoint_id: str,
    name: str | None = None,
    provider: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,  # None = leave unchanged; "" = clear the key
) -> ModelEndpoint:
    ep = _get_owned(db, user_id=user_id, endpoint_id=endpoint_id)
    if provider is not None:
        if provider not in ALLOWED_PROVIDERS:
            raise ModelError("invalid provider")
        ep.provider = provider
    if name is not None:
        ep.name = name.strip()
    if base_url is not None:
        ep.base_url = base_url.strip()
    if model is not None:
        ep.model = model.strip()
    if api_key is not None:
        ep.api_key_encrypted = crypto.encrypt(api_key)
    db.add(ep)
    db.commit()
    db.refresh(ep)
    return ep


def set_default(db: Session, *, user_id: str, endpoint_id: str) -> ModelEndpoint:
    ep = _get_owned(db, user_id=user_id, endpoint_id=endpoint_id)
    _clear_other_defaults(db, user_id=user_id, keep_id=ep.id)
    ep.is_default = True
    db.add(ep)
    db.commit()
    db.refresh(ep)
    return ep


def delete_endpoint(db: Session, *, user_id: str, endpoint_id: str) -> None:
    ep = _get_owned(db, user_id=user_id, endpoint_id=endpoint_id)
    was_default = ep.is_default
    db.delete(ep)
    db.commit()
    # If we removed the default, promote the next remaining endpoint.
    if was_default:
        remaining = list_endpoints(db, user_id=user_id)
        if remaining:
            remaining[0].is_default = True
            db.add(remaining[0])
            db.commit()


def get_default(db: Session, *, user_id: str) -> ModelEndpoint | None:
    return db.exec(
        select(ModelEndpoint).where(
            ModelEndpoint.user_id == user_id, ModelEndpoint.is_default == True  # noqa: E712
        )
    ).first()


def resolve_endpoint(db: Session, *, user_id: str, endpoint_id: str | None = None) -> ModelEndpoint | None:
    """Pick the endpoint to use: the requested one (if owned), else the user's default."""
    if endpoint_id:
        ep = db.get(ModelEndpoint, endpoint_id)
        if ep is not None and ep.user_id == user_id:  # owner check
            return ep
    return get_default(db, user_id=user_id)


def decrypt_key(ep: ModelEndpoint) -> str:
    """Plaintext API key for a server-side LLM call (F5). Never sent to the client."""
    return crypto.decrypt(ep.api_key_encrypted)
