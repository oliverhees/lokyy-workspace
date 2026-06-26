"""M3.1: /projects route — auth + owner-scoped CRUD round-trip."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401
from app.api.deps import get_current_user
from app.core import auth
from app.core.db import get_session
from app.core.workspace_fs import WorkspaceFS, get_workspace_fs
from app.main import app
from app.models.entities import User

_eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(_eng)

with Session(_eng) as _s:
    _u = auth.signup(_s, organization_name="A", email="proj@x.de", password="pw123456", display_name="P")
    _UID = _u.id


def _sess():
    with Session(_eng) as s:
        yield s


def _cu() -> User:
    with Session(_eng) as s:
        return s.get(User, _UID)


@pytest.fixture(autouse=True)
def _ov(tmp_path):
    app.dependency_overrides[get_session] = _sess
    app.dependency_overrides[get_workspace_fs] = lambda: WorkspaceFS(tmp_path)
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_projects_require_auth():
    assert client.get("/projects").status_code == 401


def test_project_crud_roundtrip():
    app.dependency_overrides[get_current_user] = _cu
    assert client.get("/projects").json() == []
    # create
    created = client.post("/projects", json={"name": "Kampagne Q3"})
    assert created.status_code == 201
    pid = created.json()["id"]
    assert created.json()["dirname"] == "kampagne-q3"
    # list shows it
    assert any(p["id"] == pid for p in client.get("/projects").json())
    # rename — display name changes, dirname stays stable
    ren = client.patch(f"/projects/{pid}", json={"name": "Kampagne Q4"})
    assert ren.status_code == 200
    assert ren.json()["name"] == "Kampagne Q4" and ren.json()["dirname"] == "kampagne-q3"
    # delete
    assert client.delete(f"/projects/{pid}").status_code == 204
    assert client.get("/projects").json() == []


def test_rename_missing_project_404():
    app.dependency_overrides[get_current_user] = _cu
    assert client.patch("/projects/nope", json={"name": "x"}).status_code == 404
