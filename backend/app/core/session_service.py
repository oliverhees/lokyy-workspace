"""Chat session service (F5): owner-scoped sessions + messages, persisted.

A ChatSession needs a workspace (the central unit of the product). Until the
workspace UI exists, every user gets one lazily-created default workspace that all
their sessions hang off — forward-compatible with multi-workspace later. All reads/
writes are scoped to user_id.
"""
from sqlmodel import Session, select

from app.models.entities import ChatMessage, ChatSession, User, Workspace, utcnow

DEFAULT_WORKSPACE_NAME = "Mein Workspace"
DEFAULT_SESSION_TITLE = "Neue Unterhaltung"
_TITLE_MAX = 60


def get_or_create_default_workspace(db: Session, *, user: User) -> Workspace:
    ws = db.exec(
        select(Workspace)
        .where(Workspace.owner_id == user.id)
        .order_by(Workspace.created_at)
    ).first()
    if ws is None:
        ws = Workspace(
            organization_id=user.organization_id,
            owner_id=user.id,
            name=DEFAULT_WORKSPACE_NAME,
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)
    return ws


def list_sessions(db: Session, *, user_id: str) -> list[ChatSession]:
    return list(
        db.exec(
            select(ChatSession)
            .where(ChatSession.owner_id == user_id)
            .order_by(ChatSession.updated_at.desc())  # most recent first
        ).all()
    )


def create_session(db: Session, *, user: User, title: str | None = None) -> ChatSession:
    ws = get_or_create_default_workspace(db, user=user)
    s = ChatSession(
        organization_id=user.organization_id,
        workspace_id=ws.id,
        owner_id=user.id,
        title=title or DEFAULT_SESSION_TITLE,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def get_owned_session(db: Session, *, user_id: str, session_id: str) -> ChatSession | None:
    s = db.get(ChatSession, session_id)
    if s is None or s.owner_id != user_id:  # owner check — no cross-tenant access
        return None
    return s


def list_messages(db: Session, *, user_id: str, session_id: str) -> list[ChatMessage]:
    if get_owned_session(db, user_id=user_id, session_id=session_id) is None:
        return []
    return list(
        db.exec(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        ).all()
    )


def add_message(db: Session, *, session_id: str, role: str, content: str,
                model_used: str | None = None) -> ChatMessage:
    m = ChatMessage(session_id=session_id, role=role, content=content, model_used=model_used)
    db.add(m)
    # touch the session so it sorts to the top — must set a value, since SQLAlchemy
    # onupdate only fires when a column actually changes.
    s = db.get(ChatSession, session_id)
    if s is not None:
        s.updated_at = utcnow()
        db.add(s)
    db.commit()
    db.refresh(m)
    return m


def maybe_autotitle(db: Session, *, session: ChatSession, first_user_message: str) -> None:
    """Give a fresh session a title from its first user message."""
    if session.title in (DEFAULT_SESSION_TITLE, "", None):
        title = first_user_message.strip().splitlines()[0][:_TITLE_MAX] if first_user_message.strip() else "Unterhaltung"
        session.title = title
        db.add(session)
        db.commit()
        db.refresh(session)


def rename_session(db: Session, *, user_id: str, session_id: str, title: str) -> ChatSession | None:
    s = get_owned_session(db, user_id=user_id, session_id=session_id)
    if s is None:
        return None
    s.title = title.strip()[:_TITLE_MAX] or s.title
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def delete_session(db: Session, *, user_id: str, session_id: str) -> bool:
    s = get_owned_session(db, user_id=user_id, session_id=session_id)
    if s is None:
        return False
    db.delete(s)  # messages cascade via FK ondelete=CASCADE
    db.commit()
    return True
