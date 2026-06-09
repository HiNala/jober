from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import AdminAuditAction
from jober_api.models.product_config import ProductConfig
from jober_api.services.admin.audit import record_admin_audit

DEFAULT_CONFIG: dict[str, dict[str, Any]] = {
    "feature_flags": {
        "discovery_enabled": True,
        "batch_scheduling_enabled": True,
        "google_oauth_enabled": True,
    },
    "announcement_banner": {
        "enabled": False,
        "text": "",
        "level": "info",
    },
    "letter_defaults": {
        "default_style": "classic",
        "default_tone": "professional",
    },
}


async def list_product_config(session: AsyncSession) -> list[dict[str, Any]]:
    stmt = select(ProductConfig).order_by(ProductConfig.key)
    rows = (await session.execute(stmt)).scalars().all()
    existing = {row.key: row for row in rows}
    items: list[dict[str, Any]] = []
    for key, default in DEFAULT_CONFIG.items():
        row = existing.get(key)
        items.append(
            {
                "key": key,
                "value": row.value if row else default,
                "updated_at": row.updated_at.isoformat() if row else None,
            }
        )
    for row in rows:
        if row.key not in DEFAULT_CONFIG:
            items.append(
                {
                    "key": row.key,
                    "value": row.value,
                    "updated_at": row.updated_at.isoformat(),
                }
            )
    return items


async def get_config_value(session: AsyncSession, key: str) -> dict[str, Any]:
    row = await session.get(ProductConfig, key)
    if row is not None:
        return row.value
    return DEFAULT_CONFIG.get(key, {})


async def set_config_value(
    session: AsyncSession,
    *,
    key: str,
    value: dict[str, Any],
    actor_user_id: uuid.UUID,
) -> ProductConfig:
    row = await session.get(ProductConfig, key)
    previous = row.value if row else DEFAULT_CONFIG.get(key, {})
    now = datetime.now(UTC)
    if row is None:
        row = ProductConfig(key=key, value=value, updated_by=actor_user_id, updated_at=now)
        session.add(row)
    else:
        row.value = value
        row.updated_by = actor_user_id
        row.updated_at = now
    await record_admin_audit(
        session,
        actor_user_id=actor_user_id,
        action=AdminAuditAction.CONFIG_CHANGED,
        resource_type="product_config",
        resource_id=key,
        message=f"Updated product config '{key}'",
        details={"previous": previous, "new": value},
    )
    await session.flush()
    return row
