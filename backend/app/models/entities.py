"""Core domain entities (M0/T0.3).

Multi-tenant by design: every tenant-owned row carries `organization_id`, and
user-owned rows additionally carry `owner_id`. Scoping is enforced via
`app.core.scoping`. Shared workspaces are modeled through `Membership`.

NOTE (security): scoping is *opt-in* at the query site. A raw query without a
scope helper would cross tenants — always go through `app.core.scoping`. A
defense-in-depth follow-up (Postgres Row-Level-Security) is tracked for later.
"""
import uuid
from datetime import datetime, timezone
from enum import Enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

# Embedding dimension (matches the default multilingual model, 384). Changing the
# model means a re-embed + migration.
EMBEDDING_DIM = 384


def _embedding_column() -> Column:
    # pgvector Vector in Postgres, JSON list in SQLite (so tests run without pgvector)
    return Column(Vector(EMBEDDING_DIM).with_variant(JSON(), "sqlite"))


def gen_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Applied to every updated_at so it refreshes on UPDATE.
_UPDATED = {"onupdate": utcnow}


class Organization(SQLModel, table=True):
    """A tenant. Owns users, workspaces and everything beneath them."""

    __tablename__ = "organizations"

    id: str = Field(default_factory=gen_id, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False, sa_column_kwargs=_UPDATED)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=gen_id, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    email: str = Field(index=True, unique=True)
    display_name: str
    password_hash: str = Field(default="")  # argon2id; empty until set
    totp_secret: str | None = Field(default=None)  # base32 TOTP secret (when 2FA set up)
    totp_enabled: bool = Field(default=False)
    is_org_admin: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False, sa_column_kwargs=_UPDATED)


class Workspace(SQLModel, table=True):
    """The central unit (context, sync, sharing). Owned by a user within an org."""

    __tablename__ = "workspaces"

    id: str = Field(default_factory=gen_id, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    owner_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    name: str
    is_shared: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False, sa_column_kwargs=_UPDATED)


class WorkspaceRole(str, Enum):
    owner = "owner"
    member = "member"
    viewer = "viewer"


class Membership(SQLModel, table=True):
    """Grants a user access to a (shared) workspace with a role."""

    __tablename__ = "memberships"

    id: str = Field(default_factory=gen_id, primary_key=True)
    workspace_id: str = Field(foreign_key="workspaces.id", index=True, ondelete="CASCADE")
    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    role: WorkspaceRole = Field(default=WorkspaceRole.member)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class UserSettings(SQLModel, table=True):
    """Per-user preferences (F3). The central settings store everything reads from.

    Owner-scoped: exactly one row per user (user_id unique). Server-side source of
    truth so preferences survive device switches and can sync later. Extend by adding
    typed fields here + a migration — the API returns the whole object.
    """

    __tablename__ = "user_settings"

    id: str = Field(default_factory=gen_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, unique=True, ondelete="CASCADE")
    language: str = Field(default="de")  # de | en
    theme: str = Field(default="dark")  # dark | light | system
    connection_default: str = Field(default="local")  # local | remote
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False, sa_column_kwargs=_UPDATED)


class ModelEndpoint(SQLModel, table=True):
    """A configured LLM endpoint (F4) — model-agnostic. Owner-scoped.

    The API key is stored ENCRYPTED (api_key_encrypted) via app.core.crypto and is
    never returned in plaintext by the API. base_url + model + provider make this
    work against any OpenAI-compatible or Anthropic endpoint (cloud or local).
    """

    __tablename__ = "model_endpoints"

    id: str = Field(default_factory=gen_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    name: str
    provider: str = Field(default="openai")  # openai (OpenAI-compatible) | anthropic
    base_url: str
    model: str
    api_key_encrypted: str = Field(default="")  # ciphertext; empty = no key (e.g. local)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False, sa_column_kwargs=_UPDATED)


class AgentContext(SQLModel, table=True):
    """Per-workspace learning context (M2.1): the agent's persona (soul) and what it
    knows about the user (user_profile), as Markdown. The Context-Assembler turns
    these into the chat system prompt. One row per workspace; Telos/memory hang off
    the same workspace later (M2.2/M2.4).
    """

    __tablename__ = "agent_contexts"

    id: str = Field(default_factory=gen_id, primary_key=True)
    workspace_id: str = Field(foreign_key="workspaces.id", index=True, unique=True, ondelete="CASCADE")
    soul: str = Field(default="")  # persona / behaviour (Markdown)
    user_profile: str = Field(default="")  # what the agent knows about the user (Markdown)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False, sa_column_kwargs=_UPDATED)


class MemoryItem(SQLModel, table=True):
    """A piece of long-term memory (M2.2): an embedded snippet the agent can recall.

    Owner-scoped via workspace. `embedding` is a pgvector column in Postgres (cosine
    search) and a JSON list in SQLite (tests use Python cosine). `kind` lets later
    slices distinguish raw messages from extracted facts (M2.3).
    """

    __tablename__ = "memory_items"

    id: str = Field(default_factory=gen_id, primary_key=True)
    workspace_id: str = Field(foreign_key="workspaces.id", index=True, ondelete="CASCADE")
    kind: str = Field(default="message")  # message | fact | note
    content: str
    embedding: list[float] = Field(default=None, sa_column=_embedding_column())
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class ChatSession(SQLModel, table=True):
    """A chat/agent/research session inside a workspace.

    Named ChatSession to avoid collision with sqlmodel.Session (the DB session).
    """

    __tablename__ = "sessions"

    id: str = Field(default_factory=gen_id, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    workspace_id: str = Field(foreign_key="workspaces.id", index=True, ondelete="CASCADE")
    owner_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    title: str = Field(default="Neue Unterhaltung")
    mode: str = Field(default="chat")  # chat | agent | research
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False, sa_column_kwargs=_UPDATED)


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: str = Field(default_factory=gen_id, primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True, ondelete="CASCADE")
    role: str  # user | assistant | system | tool
    content: str
    model_used: str | None = Field(default=None)  # which model produced an assistant message
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
