"""Central RBAC: roles, permissions, and the ``can()`` check.

Permission map is intentionally small and readable so Mission 28 can extend it.
"""

from __future__ import annotations

from enum import StrEnum

from jober_api.auth.context import AuthContext
from jober_api.models.enums import UserRole


class Permission(StrEnum):
    """Actions the API can authorize."""

    AUTHENTICATED = "authenticated"
    ADMIN_ANALYTICS_READ = "admin:analytics:read"
    ADMIN_USERS_MANAGE = "admin:users:manage"
    ADMIN_AUDIT_READ = "admin:audit:read"
    ADMIN_OPS_READ = "admin:ops:read"
    ADMIN_CONFIG_MANAGE = "admin:config:manage"


class Resource(StrEnum):
    """Resources referenced by authorization checks."""

    TENANT = "tenant"
    USER = "user"
    PRODUCT_ANALYTICS = "product_analytics"
    ADMIN_USER = "admin_user"


ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.USER: frozenset({Permission.AUTHENTICATED}),
    UserRole.ADMIN: frozenset(
        {
            Permission.AUTHENTICATED,
            Permission.ADMIN_ANALYTICS_READ,
            Permission.ADMIN_USERS_MANAGE,
            Permission.ADMIN_AUDIT_READ,
            Permission.ADMIN_OPS_READ,
            Permission.ADMIN_CONFIG_MANAGE,
        }
    ),
}


def _normalize_role(role: UserRole | str) -> UserRole:
    if isinstance(role, UserRole):
        return role
    return UserRole(role)


def can(
    actor: AuthContext,
    action: Permission,
    resource: Resource | None = None,
) -> bool:
    """Return whether ``actor`` may perform ``action`` on ``resource``."""
    granted = ROLE_PERMISSIONS.get(_normalize_role(actor.role), frozenset())
    if action not in granted:
        return False

    # Admins reach product-wide *aggregate* views only via dedicated admin endpoints.
    # They must not use admin permissions to imply cross-tenant private content access.
    return not (resource == Resource.TENANT and action != Permission.AUTHENTICATED)
