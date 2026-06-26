"""Workspace filesystem layer (M3.0): real on-disk folders, strictly scoped.

Every workspace owns a real directory ``<storage_root>/<workspace_id>/``. All file
access goes through :meth:`WorkspaceFS.resolve`, which guarantees the result stays
inside that workspace root — no ``..`` traversal, no absolute-path escape, no
symlink escape. This is the security foundation the rest of M3 (files, tree,
editor) builds on; it is owner-scoped by construction because the caller only ever
passes the workspace id it already resolved from the authenticated user.

Scope note: this layer only makes *path resolution* safe. The heavy
*tool-execution* sandbox (running ffmpeg/code against these folders, with no host
FS or network) is a separate, later concern on the agent-runtime stage (M4).
"""
import re
from pathlib import Path

from app.core.config import get_settings

# Workspace ids are uuid4 hex (see entities.gen_id). Be strict about what we are
# willing to turn into a directory name, so a crafted id can never traverse.
_SAFE_WORKSPACE_ID = re.compile(r"\A[A-Za-z0-9_-]{1,64}\Z")


class PathScopeError(Exception):
    """Raised when a path would resolve outside its workspace root."""


class WorkspaceFS:
    """Path-scoped access to per-workspace on-disk folders."""

    def __init__(self, storage_root: str | Path):
        # Resolve the root once so every comparison is against a real absolute path.
        self._root = Path(storage_root).resolve()

    @property
    def root(self) -> Path:
        return self._root

    def workspace_root(self, workspace_id: str) -> Path:
        if not _SAFE_WORKSPACE_ID.match(workspace_id or ""):
            raise PathScopeError(f"invalid workspace id: {workspace_id!r}")
        return self._root / workspace_id

    def ensure_workspace(self, workspace_id: str) -> Path:
        """Create the workspace root folder if missing; return it."""
        wr = self.workspace_root(workspace_id)
        wr.mkdir(parents=True, exist_ok=True)
        return wr

    def resolve(self, workspace_id: str, rel_path: str = "") -> Path:
        """Resolve a workspace-relative path to a real absolute path, guaranteed to
        stay inside the workspace root. Raises :class:`PathScopeError` on any escape
        (``..`` traversal, absolute path, symlink pointing outside, null byte).
        """
        wr_real = self.ensure_workspace(workspace_id).resolve()
        rel = (rel_path or "").strip()
        if "\x00" in rel:
            raise PathScopeError("null byte in path")
        # An absolute rel_path would override the join and escape — reject it.
        if rel and Path(rel).is_absolute():
            raise PathScopeError(f"absolute path not allowed: {rel!r}")
        # .resolve() collapses ``..`` and follows symlinks, so an escape via either
        # lands outside wr_real and is caught by the containment check below.
        candidate = (wr_real / rel).resolve()
        if not candidate.is_relative_to(wr_real):
            raise PathScopeError(f"path escapes workspace: {rel!r}")
        return candidate


def get_workspace_fs() -> WorkspaceFS:
    """Factory bound to the configured storage root."""
    return WorkspaceFS(get_settings().workspace_storage_root)
