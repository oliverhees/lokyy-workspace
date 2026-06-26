"""Project HTTP routes (M3.1): owner-scoped projects in the user's workspace.

Projects live in the caller's default workspace (multi-workspace UI is later). The
workspace is always derived from the authenticated user, so the route is owner-scoped
by construction. WorkspaceFS is injected as a dependency so tests can point it at a
temp dir.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core import project_service, session_service
from app.core.db import get_session
from app.core.workspace_fs import WorkspaceFS, get_workspace_fs
from app.models.entities import User

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectOut(BaseModel):
    id: str
    name: str
    dirname: str


class CreateProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class RenameProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_session),
                  user: User = Depends(get_current_user)) -> list[ProjectOut]:
    ws = session_service.get_or_create_default_workspace(db, user=user)
    return [ProjectOut(id=p.id, name=p.name, dirname=p.dirname)
            for p in project_service.list_projects(db, workspace_id=ws.id)]


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(body: CreateProjectIn, db: Session = Depends(get_session),
                   user: User = Depends(get_current_user),
                   fs: WorkspaceFS = Depends(get_workspace_fs)) -> ProjectOut:
    ws = session_service.get_or_create_default_workspace(db, user=user)
    p = project_service.create_project(db, workspace_id=ws.id, name=body.name, fs=fs)
    return ProjectOut(id=p.id, name=p.name, dirname=p.dirname)


@router.patch("/{project_id}", response_model=ProjectOut)
def rename_project(project_id: str, body: RenameProjectIn, db: Session = Depends(get_session),
                   user: User = Depends(get_current_user)) -> ProjectOut:
    p = project_service.rename_project(db, user=user, project_id=project_id, name=body.name)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
    return ProjectOut(id=p.id, name=p.name, dirname=p.dirname)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_session),
                   user: User = Depends(get_current_user),
                   fs: WorkspaceFS = Depends(get_workspace_fs)) -> None:
    if not project_service.delete_project(db, user=user, project_id=project_id, fs=fs):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
