"""T1.2: agent loop — tool-call parsing, multi-round execution, runaway/round caps."""
from app.core.agent import parse_tool_calls, run_agent
from app.core.tools import Tool, ToolRegistry, ToolResult


def _scripted_llm(responses):
    it = iter(responses)

    async def caller(_messages):
        return next(it)

    return caller


def _echo_registry():
    async def echo(args):
        return ToolResult(ok=True, content=str(args.get("text", "")))

    reg = ToolRegistry()
    reg.register(Tool(name="echo", description="echoes text", parameters={}, handler=echo))
    return reg


def test_parse_multiple_and_skip_bad_json():
    text = (
        '```tool\n{"name":"a","args":{"x":1}}\n```\n'
        "noise\n"
        "```tool\n{bad json}\n```\n"
        '```tool\n{"name":"b"}\n```'
    )
    calls = parse_tool_calls(text)
    assert [c.name for c in calls] == ["a", "b"]
    assert calls[0].args == {"x": 1}
    assert calls[1].args == {}  # missing args defaults to {}


async def test_completes_without_tools():
    r = await run_agent([], ToolRegistry(), _scripted_llm(["Kein Tool nötig."]))
    assert r.stopped_reason == "completed"
    assert r.final_text == "Kein Tool nötig."
    assert r.rounds == 1


async def test_executes_tool_then_completes():
    llm = _scripted_llm([
        '```tool\n{"name":"echo","args":{"text":"hi"}}\n```',
        "Fertig: hi",
    ])
    r = await run_agent([], _echo_registry(), llm)
    assert r.stopped_reason == "completed"
    assert r.final_text == "Fertig: hi"
    assert r.rounds == 2
    assert r.tool_events == [{"name": "echo", "args": {"text": "hi"}, "ok": True}]


async def test_runaway_on_repeated_call():
    call = '```tool\n{"name":"echo","args":{}}\n```'
    r = await run_agent([], _echo_registry(), _scripted_llm([call] * 5))
    assert r.stopped_reason == "runaway"


async def test_max_rounds_cap():
    responses = ['```tool\n{"name":"echo","args":{"i":%d}}\n```' % i for i in range(20)]
    r = await run_agent([], _echo_registry(), _scripted_llm(responses), max_rounds=5)
    assert r.stopped_reason == "max_rounds"
    assert r.rounds == 5


async def test_unknown_tool_is_reported_not_raised():
    res = await ToolRegistry().execute("nope", {})
    assert res.ok is False and "unknown tool" in res.content
