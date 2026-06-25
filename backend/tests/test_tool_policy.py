"""T1.3: tool policy/security — privileged tools are admin-only, hidden from non-admins."""
from app.core.builtin_tools import register_builtins
from app.core.tools import Tool, ToolRegistry, ToolResult


async def _ok(_args):
    return ToolResult(ok=True, content="done")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("safe", "safe tool", {}, _ok, requires_admin=False))
    reg.register(Tool("danger", "admin tool", {}, _ok, requires_admin=True))
    return reg


async def test_non_admin_blocked_from_privileged_tool():
    reg = _registry()
    res = await reg.execute("danger", {}, is_admin=False)
    assert res.ok is False and "not authorized" in res.content


async def test_admin_can_run_privileged_tool():
    reg = _registry()
    assert (await reg.execute("danger", {}, is_admin=True)).ok is True


async def test_non_admin_can_run_safe_tool():
    reg = _registry()
    assert (await reg.execute("safe", {}, is_admin=False)).ok is True


def test_schemas_hide_privileged_from_non_admin():
    reg = _registry()
    non_admin = {s["name"] for s in reg.schemas_for(is_admin=False)}
    admin = {s["name"] for s in reg.schemas_for(is_admin=True)}
    assert non_admin == {"safe"}
    assert admin == {"safe", "danger"}


async def test_builtins_shell_and_python_are_admin_only():
    reg = ToolRegistry()
    register_builtins(reg)
    # non-admin sees only current_time
    assert {s["name"] for s in reg.schemas_for(is_admin=False)} == {"current_time"}
    # non-admin is blocked from run_shell even if they try
    assert (await reg.execute("run_shell", {"command": "echo hi"}, is_admin=False)).ok is False
    # current_time works for everyone
    assert (await reg.execute("current_time", {}, is_admin=False)).ok is True
