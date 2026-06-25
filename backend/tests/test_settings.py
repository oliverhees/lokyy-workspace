"""F3: user settings service — get-or-create, updates, validation, owner isolation."""
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  (register all tables)
from app.core import auth, settings_service


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return Session(eng)


def _user(db, email="a@x.de"):
    return auth.signup(db, organization_name="Acme", email=email,
                       password="pw123456", display_name="A")


def test_get_or_create_returns_defaults_then_persists():
    db = _db()
    u = _user(db)
    s = settings_service.get_or_create_settings(db, user_id=u.id)
    assert s.language == "de" and s.theme == "dark" and s.connection_default == "local"
    # second call returns the same row (no duplicate)
    again = settings_service.get_or_create_settings(db, user_id=u.id)
    assert again.id == s.id


def test_update_settings_persists():
    db = _db()
    u = _user(db)
    s = settings_service.update_settings(db, user_id=u.id, language="en", theme="light",
                                         connection_default="remote")
    assert (s.language, s.theme, s.connection_default) == ("en", "light", "remote")
    # reload via a fresh get
    reloaded = settings_service.get_or_create_settings(db, user_id=u.id)
    assert (reloaded.language, reloaded.theme) == ("en", "light")


def test_partial_update_keeps_other_fields():
    db = _db()
    u = _user(db)
    settings_service.update_settings(db, user_id=u.id, theme="light")
    s = settings_service.update_settings(db, user_id=u.id, language="en")
    assert s.theme == "light" and s.language == "en"


def test_invalid_values_rejected():
    db = _db()
    u = _user(db)
    for kwargs in ({"language": "fr"}, {"theme": "neon"}, {"connection_default": "cloud"}):
        with pytest.raises(settings_service.SettingsError):
            settings_service.update_settings(db, user_id=u.id, **kwargs)


def test_update_profile():
    db = _db()
    u = _user(db)
    updated = settings_service.update_profile(db, user=u, display_name="  Neuer Name  ")
    assert updated.display_name == "Neuer Name"  # trimmed
    with pytest.raises(settings_service.SettingsError):
        settings_service.update_profile(db, user=u, display_name="   ")


def test_settings_are_owner_isolated():
    db = _db()
    u1 = _user(db, email="one@x.de")
    u2 = _user(db, email="two@x.de")
    settings_service.update_settings(db, user_id=u1.id, language="en")
    s2 = settings_service.get_or_create_settings(db, user_id=u2.id)
    # u2 keeps defaults — u1's change does not leak across users
    assert s2.language == "de"
