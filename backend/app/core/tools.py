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


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def schemas(self) -> list[dict]:
        return [
            {"name": t.name, "description": t.description, "parameters": t.parameters}
            for t in self._tools.values()
        ]

    async def execute(self, name: str, args: dict) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult(ok=False, content=f"unknown tool: {name}")
        try:
            return await tool.handler(args or {})
        except Exception as exc:  # tools must never crash the loop
            return ToolResult(ok=False, content=f"tool error: {exc}")
