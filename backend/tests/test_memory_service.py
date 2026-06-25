"""M2.2: memory service — store + semantic recall (SQLite/Python-cosine path).

Uses the real local embedding model (multilingual), so recall is genuinely semantic.
The first embed loads the model once; subsequent calls are fast.
"""
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.core import auth, memory_service, session_service
from app.models.entities import User


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return Session(eng)


def _workspace(db, email="a@x.de"):
    u = auth.signup(db, organization_name="Acme", email=email, password="pw123456", display_name="A")
    return session_service.get_or_create_default_workspace(db, user=db.get(User, u.id)).id


def test_add_stores_embedding():
    db = _db()
    wid = _workspace(db)
    m = memory_service.add_memory(db, workspace_id=wid, content="Ich trinke jeden Morgen Kaffee.")
    assert m.id and len(m.embedding) == 384  # default model dim


def test_semantic_recall_finds_related_memory():
    db = _db()
    wid = _workspace(db)
    memory_service.add_memory(db, workspace_id=wid, content="Ich trinke jeden Morgen Kaffee.")
    memory_service.add_memory(db, workspace_id=wid, content="Python ist meine Lieblingssprache.")
    memory_service.add_memory(db, workspace_id=wid, content="Mein Hund heißt Rex.")
    hits = memory_service.search_memories(db, workspace_id=wid, query="Welches Getränk mag ich?", k=1)
    assert hits and "Kaffee" in hits[0].content  # semantic match, not keyword


def test_memory_is_workspace_scoped():
    db = _db()
    w1 = _workspace(db, "one@x.de")
    w2 = _workspace(db, "two@x.de")
    memory_service.add_memory(db, workspace_id=w1, content="Das Geheimprojekt von Nutzer eins.")
    assert memory_service.search_memories(db, workspace_id=w2, query="Geheimprojekt", k=5) == []
