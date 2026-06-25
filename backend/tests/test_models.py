"""T0.3: entities persist and owner/org scoping isolates access (SQLite in-memory)."""
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.scoping import AccessContext, scope_to_org, scope_to_owner
from app.models.entities import (
    ChatMessage,
    ChatSession,
    Organization,
    User,
    Workspace,
)


def _engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return eng


def test_entities_and_relations_persist():
    with Session(_engine()) as s:
        org = Organization(name="Acme")
        s.add(org)
        s.commit()
        s.refresh(org)
        user = User(organization_id=org.id, email="a@example.de", display_name="A")
        s.add(user)
        s.commit()
        s.refresh(user)
        ws = Workspace(organization_id=org.id, owner_id=user.id, name="W1")
        s.add(ws)
        s.commit()
        s.refresh(ws)
        sess = ChatSession(organization_id=org.id, workspace_id=ws.id, owner_id=user.id)
        s.add(sess)
        s.commit()
        s.refresh(sess)
        s.add(ChatMessage(session_id=sess.id, role="user", content="Hallo"))
        s.commit()
        assert s.exec(select(ChatMessage)).one().content == "Hallo"


def test_owner_scoping_isolates_users():
    with Session(_engine()) as s:
        org = Organization(name="Acme")
        s.add(org)
        s.commit()
        s.refresh(org)
        u1 = User(organization_id=org.id, email="u1@x.de", display_name="U1")
        u2 = User(organization_id=org.id, email="u2@x.de", display_name="U2")
        s.add(u1)
        s.add(u2)
        s.commit()
        s.refresh(u1)
        s.refresh(u2)
        s.add(Workspace(organization_id=org.id, owner_id=u1.id, name="W1"))
        s.add(Workspace(organization_id=org.id, owner_id=u2.id, name="W2"))
        s.commit()

        ctx = AccessContext(user_id=u1.id, organization_id=org.id)
        owned = s.exec(scope_to_owner(select(Workspace), Workspace, ctx)).all()
        assert len(owned) == 1 and owned[0].owner_id == u1.id

        admin = AccessContext(user_id=u1.id, organization_id=org.id, is_org_admin=True)
        all_ws = s.exec(scope_to_owner(select(Workspace), Workspace, admin)).all()
        assert len(all_ws) == 2


def test_org_scoping_blocks_cross_tenant():
    with Session(_engine()) as s:
        org_a = Organization(name="A")
        org_b = Organization(name="B")
        s.add(org_a)
        s.add(org_b)
        s.commit()
        s.refresh(org_a)
        s.refresh(org_b)
        ua = User(organization_id=org_a.id, email="a@a.de", display_name="A")
        ub = User(organization_id=org_b.id, email="b@b.de", display_name="B")
        s.add(ua)
        s.add(ub)
        s.commit()
        s.refresh(ua)
        s.refresh(ub)
        s.add(Workspace(organization_id=org_a.id, owner_id=ua.id, name="WA"))
        s.add(Workspace(organization_id=org_b.id, owner_id=ub.id, name="WB"))
        s.commit()

        ctx_a = AccessContext(user_id=ua.id, organization_id=org_a.id, is_org_admin=True)
        visible = s.exec(scope_to_org(select(Workspace), Workspace, ctx_a)).all()
        assert len(visible) == 1 and visible[0].name == "WA"
