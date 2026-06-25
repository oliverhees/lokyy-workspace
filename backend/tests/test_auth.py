"""T0.4: auth service — registration, login, sessions, 2FA, API tokens (SQLite)."""
import pyotp
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  (register all tables)
from app.core import auth
from app.models.entities import Organization


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return Session(eng)


def _org(db):
    o = Organization(name="Acme")
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def test_register_and_authenticate():
    db = _db()
    org = _org(db)
    user = auth.register_user(db, organization_id=org.id, email="A@x.de",
                              password="pw123456", display_name="A")
    assert user.email == "a@x.de"  # normalized
    assert user.password_hash and user.password_hash != "pw123456"
    assert auth.authenticate(db, email="a@x.de", password="pw123456").id == user.id
    with pytest.raises(auth.AuthError):
        auth.authenticate(db, email="a@x.de", password="wrong")


def test_duplicate_email_rejected():
    db = _db()
    org = _org(db)
    auth.register_user(db, organization_id=org.id, email="a@x.de", password="pw123456", display_name="A")
    with pytest.raises(auth.AuthError):
        auth.register_user(db, organization_id=org.id, email="a@x.de", password="pw123456", display_name="A2")


def test_session_lifecycle():
    db = _db()
    org = _org(db)
    user = auth.register_user(db, organization_id=org.id, email="a@x.de", password="pw123456", display_name="A")
    raw = auth.create_session(db, user=user)
    assert auth.resolve_session(db, raw).id == user.id
    assert auth.resolve_session(db, "bogus") is None
    auth.revoke_session(db, raw)
    assert auth.resolve_session(db, raw) is None


def test_totp_setup_enable_and_backup_codes():
    db = _db()
    org = _org(db)
    user = auth.register_user(db, organization_id=org.id, email="a@x.de", password="pw123456", display_name="A")
    secret = auth.setup_totp(db, user=user)
    code = pyotp.TOTP(secret).now()
    assert auth.verify_totp(user, code) is True
    assert auth.verify_totp(user, "000000") is False
    backups = auth.enable_totp(db, user=user, code=pyotp.TOTP(secret).now())
    assert user.totp_enabled is True
    assert len(backups) == 8
    # backup code is single-use
    assert auth.consume_backup_code(db, user=user, code=backups[0]) is True
    assert auth.consume_backup_code(db, user=user, code=backups[0]) is False


def test_api_token_issue_and_resolve():
    db = _db()
    org = _org(db)
    user = auth.register_user(db, organization_id=org.id, email="a@x.de", password="pw123456", display_name="A")
    raw = auth.issue_api_token(db, user=user, name="CI", scopes="chat")
    assert raw.startswith("lokyy_")
    assert auth.resolve_api_token(db, raw).id == user.id
    assert auth.resolve_api_token(db, "lokyy_bogus") is None
