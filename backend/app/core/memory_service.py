"""Memory service (M2.2): store + recall embedded snippets per workspace.

Recall uses pgvector cosine distance in Postgres; for SQLite (tests) it falls back to
Python cosine over the workspace's items. Owner-scoping is via workspace_id (callers
pass the user's own workspace).
"""
import math

from sqlmodel import Session, select

from app.core import embeddings
from app.models.entities import MemoryItem


def add_memory(db: Session, *, workspace_id: str, content: str, kind: str = "message") -> MemoryItem:
    content = content.strip()
    vec = embeddings.embed_one(content)
    item = MemoryItem(workspace_id=workspace_id, content=content, kind=kind, embedding=vec)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def search_memories(db: Session, *, workspace_id: str, query: str, k: int = 5) -> list[MemoryItem]:
    if not query.strip():
        return []
    qvec = embeddings.embed_one(query)
    dialect = db.bind.dialect.name if db.bind is not None else "sqlite"
    if dialect == "postgresql":
        stmt = (
            select(MemoryItem)
            .where(MemoryItem.workspace_id == workspace_id)
            .order_by(MemoryItem.embedding.cosine_distance(qvec))  # pgvector
            .limit(k)
        )
        return list(db.exec(stmt).all())
    # SQLite / fallback: rank in Python
    items = list(db.exec(select(MemoryItem).where(MemoryItem.workspace_id == workspace_id)).all())
    items.sort(key=lambda m: _cosine(qvec, m.embedding or []), reverse=True)
    return items[:k]
