"""Auth HTTP routes: register, login (with 2FA), logout, me, 2FA, API tokens."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session

from app.api.deps import SESSION_COOKIE, get_current_user
from app.core import auth
from app.core.config import get_settings
from app.core.db import get_session
from app.models.entities import User

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


# ── Schemas (Pydantic — strict request/response contracts) ───────────────────
class RegisterIn(BaseModel):
    organization_id: str
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=1)


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str
    is_org_admin: bool
    totp_enabled: bool


class TokenEnableIn(BaseModel):
    code: str


class IssueTokenIn(BaseModel):
    name: str = "API Token"
    scopes: str = "chat"


def _set_session_cookie(resp: Response, raw: str) -> None:
    resp.set_cookie(
        SESSION_COOKIE, raw, httponly=True, samesite="lax",
        secure=settings.secure_cookies, max_age=auth.SESSION_TTL_DAYS * 86400,
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: Session = Depends(get_session)) -> User:
    try:
        return auth.register_user(
            db, organization_id=body.organization_id, email=body.email,
            password=body.password, display_name=body.display_name,
        )
    except auth.AuthError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.post("/login", response_model=UserOut)
def login(body: LoginIn, response: Response, db: Session = Depends(get_session)) -> User:
    try:
        user = auth.authenticate(db, email=body.email, password=body.password)
    except auth.AuthError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))
    if user.totp_enabled:
        if not body.totp_code or not auth.verify_totp(user, body.totp_code):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "2FA code required or invalid")
    _set_session_cookie(response, auth.create_session(db, user=user))
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, request_cookie: str | None = None,
           db: Session = Depends(get_session),
           user: User = Depends(get_current_user)) -> None:
    # Session cookie is read by the dependency chain; clear it client-side.
    response.delete_cookie(SESSION_COOKIE)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/2fa/setup")
def totp_setup(db: Session = Depends(get_session), user: User = Depends(get_current_user)) -> dict:
    secret = auth.setup_totp(db, user=user)
    return {"secret": secret, "otpauth_url": _otpauth(user.email, secret)}


@router.post("/2fa/enable")
def totp_enable(body: TokenEnableIn, db: Session = Depends(get_session),
                user: User = Depends(get_current_user)) -> dict:
    try:
        codes = auth.enable_totp(db, user=user, code=body.code)
    except auth.AuthError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return {"backup_codes": codes}


@router.post("/tokens", status_code=status.HTTP_201_CREATED)
def issue_token(body: IssueTokenIn, db: Session = Depends(get_session),
                user: User = Depends(get_current_user)) -> dict:
    raw = auth.issue_api_token(db, user=user, name=body.name, scopes=body.scopes)
    return {"token": raw, "note": "shown once — store it now"}


def _otpauth(email: str, secret: str) -> str:
    import pyotp
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="Lokyy Workspace")
