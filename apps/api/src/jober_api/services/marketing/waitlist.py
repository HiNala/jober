from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.pro_waitlist import ProWaitlistEntry


async def register_pro_waitlist(
    session: AsyncSession,
    *,
    email: str,
    consent_contact: bool,
    source: str,
) -> str:
    normalized = email.strip().lower()
    existing = await session.scalar(
        select(ProWaitlistEntry.id).where(ProWaitlistEntry.email == normalized).limit(1)
    )
    if existing is not None:
        return "already_registered"

    session.add(
        ProWaitlistEntry(
            email=normalized,
            consent_contact=consent_contact,
            source=source[:64],
        )
    )
    await session.commit()
    return "created"
