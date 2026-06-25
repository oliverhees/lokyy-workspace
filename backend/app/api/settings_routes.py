"""Settings HTTP routes (F3): owner-scoped preferences + profile.

The current user comes from the auth dependency, so every read/write is
implicitly owner-scoped — a user can only ever touch their own settings.
Inputs are validated strictly via Pydantic Literals.
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import settings_service
from app.core.db import get_session
from app.models.entities import User

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsOut(BaseModel):
    language: str
    theme: str
    connection_default: str
    # Profile is convenient to return alongside preferences for the settings page.
    display_name: str
    email: str
    is_org_admin: bool


class SettingsUpdateIn(BaseModel):
    language: Literal["de", "en"] | None = None
    theme: Literal["dark", "light", "system"] | None = None
    connection_default: Literal["local", "remote"] | None = None


class ProfileUpdateIn(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)


def _out(user: User, s) -> SettingsOut:
    return SettingsOut(
        language=s.language,
        theme=s.theme,
        connection_default=s.connection_default,
        display_name=user.display_name,
        email=user.email,
        is_org_admin=user.is_org_admin,
    )


@router.get("", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_session), user: User = Depends(get_current_user)) -> SettingsOut:
    s = settings_service.get_or_create_settings(db, user_id=user.id)
    return _out(user, s)


@router.put("", response_model=SettingsOut)
def update_settings(
    body: SettingsUpdateIn,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> SettingsOut:
    try:
        s = settings_service.update_settings(
            db, user_id=user.id, language=body.language, theme=body.theme,
            connection_default=body.connection_default,
        )
    except settings_service.SettingsError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return _out(user, s)


@router.put("/profile", response_model=SettingsOut)
def update_profile(
    body: ProfileUpdateIn,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> SettingsOut:
    try:
        user = settings_service.update_profile(db, user=user, display_name=body.display_name)
    except settings_service.SettingsError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    s = settings_service.get_or_create_settings(db, user_id=user.id)
    return _out(user, s)
