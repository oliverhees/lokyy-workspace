"""Auth service: registration, login, sessions, 2FA, API tokens (M0/T0.4).

Pure functions over a SQLModel Session — no FastAPI imports here, so it stays
unit-testable against SQLite. HTTP wiring lives in the routes layer.
"""
import secrets
from datetime import datetime, timedelta, timezone

import pyotp
from sqlmodel import Session, select

from app.core.security import (
    generate_api_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.auth import ApiToken, AuthSession, BackupCode
from app.models.entities import User, utcnow

SESSION_TTL_DAYS = 7
_SESSION_BYTES = 32
_BACKUP_CODE_COUNT = 8


class AuthError(Exception):
    """Raised on any authentication failure (kept generic to avoid leaking which step failed)."""


def register_user(db: Session, *, organization_id: str, email: str, password: str,
                  display_name: str, is_org_admin: bool = False) -> User:
    email = email.strip().lower()
    if db.exec(select(User).where(User.email == email)).first():
        raise AuthError("email already registered")
    user = User(
        organization_id=organization_id,
        email=email,
        display_name=display_name,
        password_hash=hash_password(password),
        is_org_admin=is_org_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, *, email: str, password: str) -> User:
    """Verify credentials. Does NOT check 2FA — caller handles the 2FA step."""
    user = db.exec(select(User).where(User.email == email.strip().lower())).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        raise AuthError("invalid credentials")
    return user


# ── Sessions ───────────────────────────────────────────────────────────────

def create_session(db: Session, *, user: User) -> str:
    """Create a server-side session, return the RAW token (shown once)."""
    raw = secrets.token_urlsafe(_SESSION_BYTES)
    db.add(AuthSession(
        user_id=user.id,
        token_hash=hash_token(raw),
        expires_at=utcnow() + timedelta(days=SESSION_TTL_DAYS),
    ))
    db.commit()
    return raw


def resolve_session(db: Session, raw_token: str) -> User | None:
    """Return the user for a valid, unexpired session token, else None."""
    sess = db.exec(select(AuthSession).where(AuthSession.token_hash == hash_token(raw_token))).first()
    if not sess:
        return None
    expires = sess.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        return None
    return db.get(User, sess.user_id)


def revoke_session(db: Session, raw_token: str) -> None:
    sess = db.exec(select(AuthSession).where(AuthSession.token_hash == hash_token(raw_token))).first()
    if sess:
        db.delete(sess)
        db.commit()


# ── 2FA (TOTP + backup codes) ────────────────────────────────────────────────

def setup_totp(db: Session, *, user: User) -> str:
    """Generate and store a TOTP secret (not yet enabled). Returns the secret."""
    secret = pyotp.random_base32()
    user.totp_secret = secret
    db.add(user)
    db.commit()
    return secret


def verify_totp(user: User, code: str) -> bool:
    if not user.totp_secret:
        return False
    return pyotp.TOTP(user.totp_secret).verify(code, valid_window=1)


def enable_totp(db: Session, *, user: User, code: str) -> list[str]:
    """Confirm a TOTP code, enable 2FA, and return fresh backup codes (shown once)."""
    if not verify_totp(user, code):
        raise AuthError("invalid 2FA code")
    user.totp_enabled = True
    db.add(user)
    raw_codes = [secrets.token_hex(4) for _ in range(_BACKUP_CODE_COUNT)]
    for rc in raw_codes:
        db.add(BackupCode(user_id=user.id, code_hash=hash_token(rc)))
    db.commit()
    return raw_codes


def consume_backup_code(db: Session, *, user: User, code: str) -> bool:
    bc = db.exec(select(BackupCode).where(
        BackupCode.user_id == user.id,
        BackupCode.code_hash == hash_token(code),
        BackupCode.used == False,  # noqa: E712
    )).first()
    if not bc:
        return False
    bc.used = True
    db.add(bc)
    db.commit()
    return True


# ── API tokens ───────────────────────────────────────────────────────────────

def issue_api_token(db: Session, *, user: User, name: str = "API Token",
                    scopes: str = "chat") -> str:
    raw, token_hash, prefix = generate_api_token()
    db.add(ApiToken(
        user_id=user.id, organization_id=user.organization_id,
        name=name, token_hash=token_hash, token_prefix=prefix, scopes=scopes,
    ))
    db.commit()
    return raw


def resolve_api_token(db: Session, raw_token: str) -> User | None:
    tok = db.exec(select(ApiToken).where(
        ApiToken.token_hash == hash_token(raw_token), ApiToken.is_active == True,  # noqa: E712
    )).first()
    if not tok:
        return None
    tok.last_used_at = utcnow()
    db.add(tok)
    db.commit()
    return db.get(User, tok.user_id)
