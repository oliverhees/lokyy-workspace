"""M3.0: WorkspaceFS path-scoping guard — the security foundation for M3.

These tests pin the containment guarantee: no path a caller passes may ever
resolve outside its workspace root. If any of these go red, the file layer
underneath M3.1–M3.5 is unsafe.
"""
import pytest

from app.core.workspace_fs import PathScopeError, WorkspaceFS


def test_ensure_workspace_creates_dir(tmp_path):
    fs = WorkspaceFS(tmp_path)
    wr = fs.ensure_workspace("ws1")
    assert wr.is_dir() and wr == (tmp_path / "ws1").resolve()


def test_resolve_inside_is_ok(tmp_path):
    fs = WorkspaceFS(tmp_path)
    p = fs.resolve("ws1", "notizen/idee.md")
    assert p.is_relative_to((tmp_path / "ws1").resolve())


def test_resolve_empty_returns_workspace_root(tmp_path):
    fs = WorkspaceFS(tmp_path)
    assert fs.resolve("ws1") == (tmp_path / "ws1").resolve()


def test_dotdot_traversal_rejected(tmp_path):
    fs = WorkspaceFS(tmp_path)
    with pytest.raises(PathScopeError):
        fs.resolve("ws1", "../../etc/passwd")


def test_sneaky_midpath_traversal_rejected(tmp_path):
    fs = WorkspaceFS(tmp_path)
    with pytest.raises(PathScopeError):
        fs.resolve("ws1", "a/b/../../../secret")


def test_absolute_path_rejected(tmp_path):
    fs = WorkspaceFS(tmp_path)
    with pytest.raises(PathScopeError):
        fs.resolve("ws1", "/etc/passwd")


def test_null_byte_rejected(tmp_path):
    fs = WorkspaceFS(tmp_path)
    with pytest.raises(PathScopeError):
        fs.resolve("ws1", "a\x00b")


def test_symlink_escape_rejected(tmp_path):
    fs = WorkspaceFS(tmp_path)
    wr = fs.ensure_workspace("ws1")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("top secret")
    (wr / "link").symlink_to(outside)  # symlink pointing out of the workspace
    with pytest.raises(PathScopeError):
        fs.resolve("ws1", "link/secret.txt")


def test_invalid_workspace_id_rejected(tmp_path):
    fs = WorkspaceFS(tmp_path)
    for bad in ("../evil", "ws/../..", "a b", "", "x" * 65):
        with pytest.raises(PathScopeError):
            fs.workspace_root(bad)


def test_workspaces_are_isolated(tmp_path):
    fs = WorkspaceFS(tmp_path)
    a = fs.resolve("wsA", "file.txt")
    b = fs.resolve("wsB", "file.txt")
    assert not a.is_relative_to((tmp_path / "wsB").resolve())
    assert not b.is_relative_to((tmp_path / "wsA").resolve())
