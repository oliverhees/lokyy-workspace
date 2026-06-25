"""F5: chat session service — sessions, messages, autotitle, owner isolation, cascade."""
from sqlmodel import Session, SQLModel, create_engine

from sqlalchemy import event

import app.models  # noqa: F401  (register all tables)
from app.core import auth, session_service
from app.models.entities import ChatMessage, ChatSession


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})

    # SQLite ignores FK cascades unless PRAGMA foreign_keys is on — enable it so the
    # delete-cascade behaves like Postgres in tests.
    @event.listens_for(eng, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    SQLModel.metadata.create_all(eng)
    return Session(eng)


def _user(db, email="a@x.de"):
    return auth.signup(db, organization_name="Acme", email=email,
                       password="pw123456", display_name="A")


def test_default_workspace_created_once():
    db = _db()
    u = _user(db)
    w1 = session_service.get_or_create_default_workspace(db, user=u)
    w2 = session_service.get_or_create_default_workspace(db, user=u)
    assert w1.id == w2.id and w1.owner_id == u.id


def test_create_list_and_messages():
    db = _db()
    u = _user(db)
    s = session_service.create_session(db, user=u)
    session_service.add_message(db, session_id=s.id, role="user", content="Hallo")
    session_service.add_message(db, session_id=s.id, role="assistant", content="Hi!")
    msgs = session_service.list_messages(db, user_id=u.id, session_id=s.id)
    assert [(m.role, m.content) for m in msgs] == [("user", "Hallo"), ("assistant", "Hi!")]
    assert len(session_service.list_sessions(db, user_id=u.id)) == 1


def test_autotitle_from_first_message():
    db = _db()
    u = _user(db)
    s = session_service.create_session(db, user=u)
    assert s.title == "Neue Unterhaltung"
    session_service.maybe_autotitle(db, session=s, first_user_message="Wie buche ich eine Reise?")
    assert s.title == "Wie buche ich eine Reise?"
    # does not overwrite an existing title
    session_service.maybe_autotitle(db, session=s, first_user_message="andere Frage")
    assert s.title == "Wie buche ich eine Reise?"


def test_owner_isolation_and_delete_cascade():
    db = _db()
    u1 = _user(db, email="one@x.de")
    u2 = _user(db, email="two@x.de")
    s = session_service.create_session(db, user=u1)
    session_service.add_message(db, session_id=s.id, role="user", content="x")
    # u2 cannot see or delete u1's session
    assert session_service.get_owned_session(db, user_id=u2.id, session_id=s.id) is None
    assert session_service.delete_session(db, user_id=u2.id, session_id=s.id) is False
    # u1 deletes → session gone + messages cascade
    assert session_service.delete_session(db, user_id=u1.id, session_id=s.id) is True
    from sqlmodel import select
    assert db.exec(select(ChatSession)).first() is None
    assert db.exec(select(ChatMessage)).first() is None
