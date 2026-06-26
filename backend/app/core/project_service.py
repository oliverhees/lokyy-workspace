"""Project service (M3.1): projects inside a workspace, each a real on-disk folder.

A project is a workspace subfolder plus (later, M3.4) an assigned context. The
folder name (`dirname`) is slugged once at creation and stays stable across renames,
so paths never break; the display `name` is freely renameable. Owner-scoping runs
through the workspace owner — a project is reachable only by its workspace's owner.
All folder access goes through WorkspaceFS (path-scoped, M3.0).
"""
import re
import shutil

from sqlmodel import Session, select

from app.core.workspace_fs import WorkspaceFS, get_workspace_fs
from app.models.entities import Project, User, Workspace

_NAME_MAX = 120
_SLUG_MAX = 48


def _slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return s[:_SLUG_MAX].strip("-") or "projekt"


def _unique_dirname(db: Session, workspace_id: str, base: str) -> str:
    existing = {
        p.dirname for p in db.exec(
            select(Project).where(Project.workspace_id == workspace_id)
        ).all()
    }
    if base not in existing:
        return base
    i = 2
    while f"{base}-{i}" in existing:
        i += 1
    return f"{base}-{i}"


def create_project(db: Session, *, workspace_id: str, name: str,
                   fs: WorkspaceFS | None = None) -> Project:
    fs = fs or get_workspace_fs()
    name = name.strip()[:_NAME_MAX] or "Neues Projekt"
    dirname = _unique_dirname(db, workspace_id, _slugify(name))
    fs.resolve(workspace_id, dirname).mkdir(parents=True, exist_ok=True)  # real folder
    p = Project(workspace_id=workspace_id, name=name, dirname=dirname)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def list_projects(db: Session, *, workspace_id: str) -> list[Project]:
    return list(db.exec(
        select(Project)
        .where(Project.workspace_id == workspace_id)
        .order_by(Project.created_at)
    ).all())


def get_owned_project(db: Session, *, user: User, project_id: str) -> Project | None:
    p = db.get(Project, project_id)
    if p is None:
        return None
    ws = db.get(Workspace, p.workspace_id)
    if ws is None or ws.owner_id != user.id:  # cross-tenant guard
        return None
    return p


def rename_project(db: Session, *, user: User, project_id: str, name: str) -> Project | None:
    p = get_owned_project(db, user=user, project_id=project_id)
    if p is None:
        return None
    p.name = name.strip()[:_NAME_MAX] or p.name  # dirname stays stable
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def delete_project(db: Session, *, user: User, project_id: str,
                   fs: WorkspaceFS | None = None) -> bool:
    p = get_owned_project(db, user=user, project_id=project_id)
    if p is None:
        return False
    fs = fs or get_workspace_fs()
    folder = fs.resolve(p.workspace_id, p.dirname)  # resolve-guarded, inside workspace
    if folder.is_dir():
        shutil.rmtree(folder)
    db.delete(p)
    db.commit()
    return True
