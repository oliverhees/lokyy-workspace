"""Tool interface + registry (M1/T1.2 minimal core).

A Tool is a named, schema-described async handler. T1.3 extends this with policy,
owner/admin security and concrete tool implementations; here we keep the contract
small so the agent loop can drive it.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass
class ToolResult:
    ok: bool
    content: str


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict  # JSON Schema for the args
    handler: Callable[[dict], Awaitable[ToolResult]]
    requires_admin: bool = False  # privileged tools (shell, code, file write …)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def _schema(self, t: Tool) -> dict:
        return {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters,
            "requires_admin": t.requires_admin,
        }

    def schemas(self) -> list[dict]:
        return [self._schema(t) for t in self._tools.values()]

    def schemas_for(self, *, is_admin: bool) -> list[dict]:
        """Only the tools the caller may use — privileged tools are hidden from non-admins."""
        return [self._schema(t) for t in self._tools.values() if is_admin or not t.requires_admin]

    async def execute(self, name: str, args: dict, *, is_admin: bool = False) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult(ok=False, content=f"unknown tool: {name}")
        if tool.requires_admin and not is_admin:
            # Security: never run a privileged tool for a non-admin (defense in depth —
            # such tools are also hidden from the prompt via schemas_for()).
            return ToolResult(ok=False, content=f"not authorized: '{name}' requires admin")
        try:
            return await tool.handler(args or {})
        except Exception as exc:  # tools must never crash the loop
            return ToolResult(ok=False, content=f"tool error: {exc}")
