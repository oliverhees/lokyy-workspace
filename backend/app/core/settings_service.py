"""User settings service (F3): owner-scoped preferences + profile updates.

Pure functions over a SQLModel Session (unit-testable against SQLite). Settings
are get-or-created lazily so every user has a row on first read. HTTP wiring and
strict input validation (Pydantic Literals) live in the routes layer; these
guards are defense-in-depth.
"""
from sqlmodel import Session, select

from app.models.entities import User, UserSettings

ALLOWED_LANGUAGES = {"de", "en"}
ALLOWED_THEMES = {"dark", "light", "system"}
ALLOWED_CONNECTIONS = {"local", "remote"}


class SettingsError(Exception):
    """Raised on an invalid settings value."""


def get_or_create_settings(db: Session, *, user_id: str) -> UserSettings:
    s = db.exec(select(UserSettings).where(UserSettings.user_id == user_id)).first()
    if s is None:
        s = UserSettings(user_id=user_id)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def update_settings(
    db: Session,
    *,
    user_id: str,
    language: str | None = None,
    theme: str | None = None,
    connection_default: str | None = None,
) -> UserSettings:
    s = get_or_create_settings(db, user_id=user_id)
    if language is not None:
        if language not in ALLOWED_LANGUAGES:
            raise SettingsError("invalid language")
        s.language = language
    if theme is not None:
        if theme not in ALLOWED_THEMES:
            raise SettingsError("invalid theme")
        s.theme = theme
    if connection_default is not None:
        if connection_default not in ALLOWED_CONNECTIONS:
            raise SettingsError("invalid connection_default")
        s.connection_default = connection_default
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def update_profile(db: Session, *, user: User, display_name: str) -> User:
    name = display_name.strip()
    if not name:
        raise SettingsError("display_name must not be empty")
    user.display_name = name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
