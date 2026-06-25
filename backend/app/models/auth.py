"""Auth-related persistence: sessions, API tokens, 2FA backup codes (M0/T0.4).

Server-side sessions and tokens store only *hashes*, never the raw secret — the
raw value is shown to the client once and never persisted.
"""
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.entities import gen_id, utcnow


class AuthSession(SQLModel, table=True):
    """A logged-in browser session (revocable, server-side)."""

    __tablename__ = "auth_sessions"

    id: str = Field(default_factory=gen_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    token_hash: str = Field(index=True, unique=True)  # sha256 of the session token
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    last_seen_at: datetime = Field(default_factory=utcnow, nullable=False)


class ApiToken(SQLModel, table=True):
    """A programmatic access token (hashed; scoped)."""

    __tablename__ = "api_tokens"

    id: str = Field(default_factory=gen_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    organization_id: str = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    name: str = Field(default="API Token")
    token_hash: str = Field(index=True, unique=True)
    token_prefix: str  # first chars, for display only
    scopes: str = Field(default="chat")  # comma-separated; "chat" | "admin" | ...
    is_active: bool = Field(default=True)
    last_used_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class BackupCode(SQLModel, table=True):
    """A single-use 2FA backup code (stored hashed)."""

    __tablename__ = "backup_codes"

    id: str = Field(default_factory=gen_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    code_hash: str = Field(index=True)
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
