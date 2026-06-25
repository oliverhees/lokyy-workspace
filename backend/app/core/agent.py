"""Agent loop: multi-round tool-calling orchestration (M1/T1.2).

The LLM requests tools by emitting a fenced block:

    ```tool
    {"name": "search", "args": {"q": "..."}}
    ```

This text protocol is provider-agnostic — it works with models that have no native
tool-calling (important for small local models). Native tool-call support can be
layered on later. The loop runs LLM → parse → execute → feed results → repeat, with
a hard round cap and repeated-call (runaway) detection.
"""
from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from app.core.tools import ToolRegistry

LLMCaller = Callable[[list[dict]], Awaitable[str]]

_TOOL_BLOCK = re.compile(r"```tool\s*\n(.*?)```", re.DOTALL)

DEFAULT_MAX_ROUNDS = 10
RUNAWAY_REPEAT_THRESHOLD = 3  # identical call repeated this many times → stop


@dataclass
class ToolCall:
    name: str
    args: dict


@dataclass
class AgentResult:
    final_text: str
    rounds: int
    messages: list[dict]
    stopped_reason: str  # "completed" | "max_rounds" | "runaway"
    tool_events: list[dict] = field(default_factory=list)


def parse_tool_calls(text: str) -> list[ToolCall]:
    """Extract fenced ```tool {...}``` blocks into ToolCalls (bad JSON is skipped)."""
    calls: list[ToolCall] = []
    for match in _TOOL_BLOCK.finditer(text):
        try:
            obj = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("name"), str):
            args = obj.get("args", {})
            calls.append(ToolCall(name=obj["name"], args=args if isinstance(args, dict) else {}))
    return calls


def _signature(call: ToolCall) -> str:
    return call.name + json.dumps(call.args, sort_keys=True)


async def run_agent(
    messages: list[dict],
    registry: ToolRegistry,
    llm: LLMCaller,
    *,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    is_admin: bool = False,
) -> AgentResult:
    convo = list(messages)
    tool_events: list[dict] = []
    seen: dict[str, int] = {}

    for round_index in range(max_rounds):
        response = await llm(convo)
        convo.append({"role": "assistant", "content": response})
        calls = parse_tool_calls(response)

        if not calls:
            return AgentResult(response, round_index + 1, convo, "completed", tool_events)

        for call in calls:
            sig = _signature(call)
            seen[sig] = seen.get(sig, 0) + 1
            if seen[sig] >= RUNAWAY_REPEAT_THRESHOLD:
                return AgentResult(
                    f"(stopped: repeated call to '{call.name}')",
                    round_index + 1, convo, "runaway", tool_events,
                )
            result = await registry.execute(call.name, call.args, is_admin=is_admin)
            tool_events.append({"name": call.name, "args": call.args, "ok": result.ok})
            convo.append({
                "role": "tool",
                "content": f"[{call.name}] {'OK' if result.ok else 'ERR'}: {result.content}",
            })

    return AgentResult("(stopped: max rounds reached)", max_rounds, convo, "max_rounds", tool_events)
