"""T1.4: RAG-style tool selection — relevance ranking + admin policy (fake embeddings)."""
from app.core.builtin_tools import register_builtins
from app.core.tool_selection import ToolSelector, cosine
from app.core.tools import Tool, ToolRegistry, ToolResult

# Deterministic keyword embedding (no model download needed in tests).
_VOCAB = ["time", "shell", "python", "email", "weather"]


def _fake_embed(texts: list[str]) -> list[list[float]]:
    out = []
    for t in texts:
        tl = t.lower()
        out.append([1.0 if word in tl else 0.0 for word in _VOCAB])
    return out


async def _noop(_a):
    return ToolResult(ok=True, content="")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("current_time", "current time clock", {}, _noop))
    reg.register(Tool("send_email", "send email message", {}, _noop))
    reg.register(Tool("get_weather", "weather forecast", {}, _noop))
    return reg


def test_cosine_basics():
    assert cosine([1, 0], [1, 0]) == 1.0
    assert cosine([1, 0], [0, 1]) == 0.0


def test_selects_most_relevant_tool():
    sel = ToolSelector(_registry(), _fake_embed)
    top = sel.select("what time is it", is_admin=True, k=1)
    assert [s["name"] for s in top] == ["current_time"]
    top = sel.select("send an email to my client", is_admin=True, k=1)
    assert [s["name"] for s in top] == ["send_email"]


def test_k_limits_results():
    sel = ToolSelector(_registry(), _fake_embed)
    assert len(sel.select("email", is_admin=True, k=2)) <= 2


def test_respects_admin_policy():
    reg = ToolRegistry()
    register_builtins(reg)  # run_shell/run_python are admin-only
    sel = ToolSelector(reg, _fake_embed)
    names = {s["name"] for s in sel.select("run a shell command", is_admin=False, k=10)}
    assert "run_shell" not in names and "run_python" not in names
    admin_names = {s["name"] for s in sel.select("run a shell command", is_admin=True, k=10)}
    assert "run_shell" in admin_names
