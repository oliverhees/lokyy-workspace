"""Built-in tools + their policy (M1/T1.3).

Privileged tools (shell, python) are admin-only — mirroring the odysseus trust model
where shell/code execution is never available to non-admins. They run inside the
T1.5 sandbox (timeout, output cap, isolated cwd, scrubbed env).
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.core import sandbox
from app.core.tools import Tool, ToolRegistry, ToolResult


async def _run_shell(args: dict) -> ToolResult:
    cmd = str(args.get("command", "")).strip()
    if not cmd:
        return ToolResult(ok=False, content="command is required")
    res = await sandbox.run_shell(cmd, timeout=args.get("timeout", 30))
    body = res.stdout if res.ok else f"{res.stdout}\n{res.stderr}".strip()
    return ToolResult(ok=res.ok, content=body or ("(timed out)" if res.timed_out else "(no output)"))


async def _run_python(args: dict) -> ToolResult:
    code = str(args.get("code", ""))
    if not code.strip():
        return ToolResult(ok=False, content="code is required")
    res = await sandbox.run_python(code, timeout=args.get("timeout", 30))
    body = res.stdout if res.ok else f"{res.stdout}\n{res.stderr}".strip()
    return ToolResult(ok=res.ok, content=body or ("(timed out)" if res.timed_out else "(no output)"))


async def _current_time(_args: dict) -> ToolResult:
    return ToolResult(ok=True, content=datetime.now(timezone.utc).isoformat())


def register_builtins(registry: ToolRegistry) -> None:
    """Register the default tool set onto a registry."""
    registry.register(Tool(
        name="current_time",
        description="Returns the current UTC time (ISO 8601).",
        parameters={"type": "object", "properties": {}},
        handler=_current_time,
        requires_admin=False,
    ))
    registry.register(Tool(
        name="run_shell",
        description="Run a shell command in the sandbox. Admin only.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "number"},
            },
            "required": ["command"],
        },
        handler=_run_shell,
        requires_admin=True,
    ))
    registry.register(Tool(
        name="run_python",
        description="Execute Python code in the sandbox. Admin only.",
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "timeout": {"type": "number"},
            },
            "required": ["code"],
        },
        handler=_run_python,
        requires_admin=True,
    ))
