"""Database engine & session management (SQLModel over the configured URL)."""
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping avoids stale connections after DB restarts.
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: yields a scoped DB session."""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Create tables from metadata (dev convenience; production uses Alembic)."""
    import app.models  # noqa: F401  (register tables)

    SQLModel.metadata.create_all(engine)
