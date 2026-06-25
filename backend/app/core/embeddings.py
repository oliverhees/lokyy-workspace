"""Embeddings for memory (M2.2) — pluggable.

Default: local fastembed (offline, DSGVO-friendly, no per-call cost). Optional: cloud
via LiteLLM (`embedding_provider="cloud"`). The model is loaded lazily and cached so
the first embed pays the load cost once. Dimension must match `settings.embedding_dim`
(and the DB Vector column) — switching models means a re-embed.
"""
from functools import lru_cache

from app.core.config import get_settings


@lru_cache(maxsize=2)
def _local_model(model_name: str):
    from fastembed import TextEmbedding  # lazy: heavy import / model load

    return TextEmbedding(model_name=model_name)


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts → list of float vectors (len == settings.embedding_dim)."""
    if not texts:
        return []
    s = get_settings()
    if s.embedding_provider == "cloud":
        import litellm

        resp = litellm.embedding(model=s.embedding_model_cloud, input=texts)
        return [list(d["embedding"]) for d in resp.data]
    model = _local_model(s.embedding_model_local)
    return [list(map(float, v)) for v in model.embed(texts)]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]
