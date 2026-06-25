"""FastAPI auth dependencies: resolve the current user from token or session."""
from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core import auth
from app.core.db import get_session
from app.models.entities import User

SESSION_COOKIE = "lokyy_session"


def get_current_user(request: Request, db: Session = Depends(get_session)) -> User:
    """Authenticate via Bearer API token first, then the session cookie."""
    authz = request.headers.get("authorization", "")
    if authz.startswith("Bearer "):
        user = auth.resolve_api_token(db, authz[7:].strip())
        if user:
            return user

    raw = request.cookies.get(SESSION_COOKIE)
    if raw:
        user = auth.resolve_session(db, raw)
        if user:
            return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
