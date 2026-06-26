"""M3.1: project service — owner-scoped projects backed by real folders."""
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.core import auth, project_service, session_service
from app.core.workspace_fs import WorkspaceFS
from app.models.entities import User


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return Session(eng)


def _user(db, email="a@x.de"):
    u = auth.signup(db, organization_name="Acme", email=email, password="pw123456", display_name="A")
    return db.get(User, u.id)


def _ws(db, user):
    return session_service.get_or_create_default_workspace(db, user=user).id


def test_create_makes_db_row_and_real_folder(tmp_path):
    db = _db(); fs = WorkspaceFS(tmp_path)
    u = _user(db); wid = _ws(db, u)
    p = project_service.create_project(db, workspace_id=wid, name="Mein Video Projekt", fs=fs)
    assert p.id and p.name == "Mein Video Projekt"
    assert p.dirname == "mein-video-projekt"
    assert fs.resolve(wid, p.dirname).is_dir()  # real folder created on disk


def test_dirname_is_unique_per_workspace(tmp_path):
    db = _db(); fs = WorkspaceFS(tmp_path)
    u = _user(db); wid = _ws(db, u)
    a = project_service.create_project(db, workspace_id=wid, name="Report", fs=fs)
    b = project_service.create_project(db, workspace_id=wid, name="Report", fs=fs)
    assert a.dirname == "report" and b.dirname == "report-2"


def test_rename_keeps_dirname_stable(tmp_path):
    db = _db(); fs = WorkspaceFS(tmp_path)
    u = _user(db); wid = _ws(db, u)
    p = project_service.create_project(db, workspace_id=wid, name="Alt", fs=fs)
    r = project_service.rename_project(db, user=u, project_id=p.id, name="Ganz neuer Name")
    assert r.name == "Ganz neuer Name" and r.dirname == "alt"  # folder ref stays put


def test_delete_removes_row_and_folder(tmp_path):
    db = _db(); fs = WorkspaceFS(tmp_path)
    u = _user(db); wid = _ws(db, u)
    p = project_service.create_project(db, workspace_id=wid, name="Weg damit", fs=fs)
    folder = fs.resolve(wid, p.dirname)
    assert folder.is_dir()
    assert project_service.delete_project(db, user=u, project_id=p.id, fs=fs) is True
    assert not folder.exists()
    assert project_service.get_owned_project(db, user=u, project_id=p.id) is None


def test_projects_are_owner_scoped(tmp_path):
    db = _db(); fs = WorkspaceFS(tmp_path)
    a = _user(db, "a@x.de"); wsa = _ws(db, a)
    b = _user(db, "b@x.de")
    p = project_service.create_project(db, workspace_id=wsa, name="Geheim", fs=fs)
    # user B cannot reach user A's project via any operation
    assert project_service.get_owned_project(db, user=b, project_id=p.id) is None
    assert project_service.rename_project(db, user=b, project_id=p.id, name="hack") is None
    assert project_service.delete_project(db, user=b, project_id=p.id, fs=fs) is False
    # ... and A's project (and its folder) is untouched
    assert fs.resolve(wsa, p.dirname).is_dir()
