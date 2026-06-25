"""Agent context HTTP routes (M2.1): read/write the workspace soul + user profile.

Scoped to the caller's (default) workspace, so it's owner-scoped by construction.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import context_service, session_service
from app.core.db import get_session
from app.models.entities import User

router = APIRouter(prefix="/context", tags=["context"])


class ContextOut(BaseModel):
    soul: str
    user_profile: str


class ContextUpdateIn(BaseModel):
    soul: str | None = None
    user_profile: str | None = None


def _workspace_id(db: Session, user: User) -> str:
    return session_service.get_or_create_default_workspace(db, user=user).id


@router.get("", response_model=ContextOut)
def get_context(db: Session = Depends(get_session), user: User = Depends(get_current_user)) -> ContextOut:
    ctx = context_service.get_or_create_context(db, workspace_id=_workspace_id(db, user))
    return ContextOut(soul=ctx.soul, user_profile=ctx.user_profile)


@router.put("", response_model=ContextOut)
def update_context(body: ContextUpdateIn, db: Session = Depends(get_session),
                   user: User = Depends(get_current_user)) -> ContextOut:
    ctx = context_service.update_context(
        db, workspace_id=_workspace_id(db, user), soul=body.soul, user_profile=body.user_profile,
    )
    return ContextOut(soul=ctx.soul, user_profile=ctx.user_profile)
