"""Owner / organization scoping — the multi-tenant access guard.

Every query for tenant data must be passed through one of these helpers so a
user can never read across organizations, and non-admins only see their own
rows (plus shared workspaces they're a member of, handled at the query site).
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccessContext:
    """Who is asking. Built from the authenticated session (added in T0.4)."""

    user_id: str
    organization_id: str
    is_org_admin: bool = False


def scope_to_org(statement: Any, model: Any, ctx: AccessContext) -> Any:
    """Restrict to the caller's organization (tenant isolation — always)."""
    return statement.where(model.organization_id == ctx.organization_id)


def scope_to_owner(statement: Any, model: Any, ctx: AccessContext) -> Any:
    """Restrict to rows the caller owns.

    Org admins see everything in their org; everyone else only their own rows.
    Always also tenant-isolated.

    NOTE: this does NOT yet include shared workspaces the caller is a member of
    (via Membership) — that access path is added with M7 (Sync & Team). Until
    then, owner-only + org-admin are the access rules.
    """
    statement = scope_to_org(statement, model, ctx)
    if ctx.is_org_admin:
        return statement
    return statement.where(model.owner_id == ctx.user_id)
