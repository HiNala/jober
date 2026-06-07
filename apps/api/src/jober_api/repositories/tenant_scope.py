from __future__ import annotations

import uuid

from sqlalchemy import Select

from jober_api.db.base import Base


def scope_stmt[T: Base](
    stmt: Select[tuple[T]], model: type[T], tenant_id: uuid.UUID | None
) -> Select[tuple[T]]:
    if tenant_id is None:
        return stmt
    return stmt.where(model.tenant_id == tenant_id)  # type: ignore[attr-defined]


def belongs_to_tenant(entity: Base | None, tenant_id: uuid.UUID | None) -> bool:
    if entity is None:
        return False
    if tenant_id is None:
        return True
    entity_tenant = getattr(entity, "tenant_id", None)
    return entity_tenant == tenant_id
