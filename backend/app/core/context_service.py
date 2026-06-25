"""Agent context service + Context-Assembler (M2.1).

Holds the per-workspace persona (soul) and user profile, and assembles them into the
chat system prompt. This is the seam the rest of M2 plugs into: memory (M2.2) and
Telos (M2.4) will append further sections in `assemble_system_prompt`.
"""
from sqlmodel import Session, select

from app.models.entities import AgentContext

# A sensible default persona so a fresh workspace already behaves well.
DEFAULT_SOUL = (
    "Du bist Lokyy, der persönliche KI-Assistent für Selbstständige und kleine "
    "Unternehmen. Antworte klar, präzise und auf Deutsch (außer der Nutzer schreibt "
    "in einer anderen Sprache). Sei hilfsbereit und konkret, frag nach, wenn etwas "
    "unklar ist, und halte dich kurz, wenn eine kurze Antwort reicht."
)


def get_or_create_context(db: Session, *, workspace_id: str) -> AgentContext:
    ctx = db.exec(
        select(AgentContext).where(AgentContext.workspace_id == workspace_id)
    ).first()
    if ctx is None:
        ctx = AgentContext(workspace_id=workspace_id, soul=DEFAULT_SOUL)
        db.add(ctx)
        db.commit()
        db.refresh(ctx)
    return ctx


def update_context(
    db: Session,
    *,
    workspace_id: str,
    soul: str | None = None,
    user_profile: str | None = None,
) -> AgentContext:
    ctx = get_or_create_context(db, workspace_id=workspace_id)
    if soul is not None:
        ctx.soul = soul
    if user_profile is not None:
        ctx.user_profile = user_profile
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx


def assemble_system_prompt(ctx: AgentContext) -> str:
    """Build the system prompt from the workspace context. Empty sections are skipped.

    Extension point for M2: memory snippets and Telos get appended here later.
    """
    parts: list[str] = []
    soul = (ctx.soul or "").strip()
    profile = (ctx.user_profile or "").strip()
    parts.append(soul or DEFAULT_SOUL)
    if profile:
        parts.append("# Was du über den Nutzer weißt\n" + profile)
    return "\n\n".join(parts)
