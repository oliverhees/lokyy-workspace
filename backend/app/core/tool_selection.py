"""RAG-style tool selection (M1/T1.4).

Only the most relevant tools are put into the prompt — this keeps the context small,
which matters a lot for small local models (odysseus solved the same "agent prompt
bloat" problem with a ChromaDB tool index).

Embeddings are pluggable (`EmbedFn`). The default uses fastembed (local ONNX, no API
key). Selection ranks by cosine similarity.

Design note: for the *small* set of tools (tens, not thousands) in-memory cosine is the
right tool — fast, no DB round-trip. The same `EmbedFn` abstraction backs the large
Memory/RAG layer in M2, which *is* where pgvector belongs (thousands of chunks). So this
is "RAG-style selection", pgvector-ready, but deliberately not over-engineered here.
"""
from __future__ import annotations

import math
from collections.abc import Callable

from app.core.tools import ToolRegistry

EmbedFn = Callable[[list[str]], list[list[float]]]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class ToolSelector:
    """Selects the top-k relevant, *permitted* tools for a query."""

    def __init__(self, registry: ToolRegistry, embed_fn: EmbedFn):
        self.registry = registry
        self.embed = embed_fn
        self._index: dict[str, list[float]] = {}

    def build_index(self) -> None:
        tools = self.registry.schemas()
        if not tools:
            self._index = {}
            return
        texts = [f"{t['name']}: {t['description']}" for t in tools]
        vectors = self.embed(texts)
        self._index = {t["name"]: v for t, v in zip(tools, vectors)}

    def select(self, query: str, *, is_admin: bool, k: int = 5) -> list[dict]:
        """Return up to k tool schemas, most relevant first, respecting admin policy."""
        if not self._index:
            self.build_index()
        permitted = {s["name"]: s for s in self.registry.schemas_for(is_admin=is_admin)}
        if not permitted:
            return []
        query_vec = self.embed([query])[0]
        ranked = sorted(
            ((name, cosine(query_vec, vec)) for name, vec in self._index.items() if name in permitted),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [permitted[name] for name, _ in ranked[:k]]


def default_embedder() -> EmbedFn:
    """Lazy fastembed (local ONNX, all-MiniLM). Raises a clear error if not installed."""
    try:
        from fastembed import TextEmbedding
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "fastembed not installed — `pip install fastembed`, or inject a custom embed_fn"
        ) from exc

    model = TextEmbedding()

    def embed(texts: list[str]) -> list[list[float]]:
        return [list(v) for v in model.embed(texts)]

    return embed
