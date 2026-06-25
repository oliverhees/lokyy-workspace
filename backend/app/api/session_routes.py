"""Chat session HTTP routes (F5): owner-scoped session + message management."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import session_service
from app.core.db import get_session
from app.models.entities import User

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionOut(BaseModel):
    id: str
    title: str


class MessageOut(BaseModel):
    role: str
    content: str


class CreateSessionIn(BaseModel):
    title: str | None = None


class RenameIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)


@router.get("", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list[SessionOut]:
    return [SessionOut(id=s.id, title=s.title) for s in session_service.list_sessions(db, user_id=user.id)]


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(body: CreateSessionIn, db: Session = Depends(get_session),
                   user: User = Depends(get_current_user)) -> SessionOut:
    s = session_service.create_session(db, user=user, title=body.title)
    return SessionOut(id=s.id, title=s.title)


@router.get("/{session_id}/messages", response_model=list[MessageOut])
def get_messages(session_id: str, db: Session = Depends(get_session),
                 user: User = Depends(get_current_user)) -> list[MessageOut]:
    if session_service.get_owned_session(db, user_id=user.id, session_id=session_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "session not found")
    msgs = session_service.list_messages(db, user_id=user.id, session_id=session_id)
    return [MessageOut(role=m.role, content=m.content) for m in msgs]


@router.patch("/{session_id}", response_model=SessionOut)
def rename(session_id: str, body: RenameIn, db: Session = Depends(get_session),
           user: User = Depends(get_current_user)) -> SessionOut:
    s = session_service.rename_session(db, user_id=user.id, session_id=session_id, title=body.title)
    if s is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "session not found")
    return SessionOut(id=s.id, title=s.title)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(session_id: str, db: Session = Depends(get_session),
           user: User = Depends(get_current_user)) -> None:
    if not session_service.delete_session(db, user_id=user.id, session_id=session_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "session not found")
