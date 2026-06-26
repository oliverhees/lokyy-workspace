"""M2.1: agent context service + system-prompt assembler."""
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.core import auth, context_service, session_service
from app.models.entities import User


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return Session(eng)


def _workspace(db, email="a@x.de"):
    u = auth.signup(db, organization_name="Acme", email=email, password="pw123456", display_name="A")
    return session_service.get_or_create_default_workspace(db, user=db.get(User, u.id)).id


def test_get_or_create_seeds_default_soul():
    db = _db()
    wid = _workspace(db)
    ctx = context_service.get_or_create_context(db, workspace_id=wid)
    assert ctx.soul == context_service.DEFAULT_SOUL and ctx.user_profile == ""
    # idempotent
    assert context_service.get_or_create_context(db, workspace_id=wid).id == ctx.id


def test_update_and_persist():
    db = _db()
    wid = _workspace(db)
    context_service.update_context(db, workspace_id=wid, soul="Sei knapp.", user_profile="Heißt Oliver.")
    ctx = context_service.get_or_create_context(db, workspace_id=wid)
    assert ctx.soul == "Sei knapp." and ctx.user_profile == "Heißt Oliver."


def test_assemble_system_prompt():
    db = _db()
    wid = _workspace(db)
    ctx = context_service.update_context(db, workspace_id=wid, soul="Sei knapp.", user_profile="Heißt Oliver.")
    prompt = context_service.assemble_system_prompt(ctx)
    assert "Sei knapp." in prompt
    assert "Was du über den Nutzer weißt" in prompt and "Heißt Oliver." in prompt
    # empty profile → no user section; empty soul → default soul
    ctx2 = context_service.update_context(db, workspace_id=wid, soul="", user_profile="")
    p2 = context_service.assemble_system_prompt(ctx2)
    assert context_service.DEFAULT_SOUL in p2 and "Was du über den Nutzer weißt" not in p2


def test_telos_in_system_prompt():
    db = _db()
    wid = _workspace(db)
    ctx = context_service.update_context(db, workspace_id=wid, telos="Mission: 1000 Kunden helfen.")
    prompt = context_service.assemble_system_prompt(ctx)
    assert "Telos" in prompt and "1000 Kunden" in prompt
    # empty telos → no telos section
    ctx2 = context_service.update_context(db, workspace_id=wid, telos="")
    assert "Telos" not in context_service.assemble_system_prompt(ctx2)


def test_context_is_workspace_scoped():
    """Cross-Tenant (M2 QA, LWS-65): workspace B's context never carries workspace A's data.

    assemble_system_prompt reads only the ctx it is handed, so the tenant guarantee
    lives in get_or_create_context(workspace_id=...). This pins it against a future
    refactor that might drop the workspace filter and silently leak across tenants.
    """
    db = _db()
    w1 = _workspace(db, "one@x.de")
    w2 = _workspace(db, "two@x.de")
    context_service.update_context(
        db, workspace_id=w1, soul="Sei knapp.",
        user_profile="Heißt Alice, Geheimprojekt Zeta.",
        telos="Mission: Markt erobern.",
    )
    # Workspace B is fresh and isolated.
    ctx2 = context_service.get_or_create_context(db, workspace_id=w2)
    assert ctx2.soul == context_service.DEFAULT_SOUL
    assert ctx2.user_profile == ""
    assert (ctx2.telos or "") == ""
    # And none of workspace A's secrets surface in workspace B's assembled prompt.
    prompt2 = context_service.assemble_system_prompt(ctx2)
    for secret in ("Geheimprojekt Zeta", "Alice", "Markt erobern"):
        assert secret not in prompt2
