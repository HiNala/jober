from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.run_event import RunEvent
from jober_api.repositories.base import Repository


class RunEventRepository(Repository[RunEvent]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RunEvent)

    async def next_seq(self, run_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.max(RunEvent.seq), 0)).where(RunEvent.run_id == run_id)
        current = (await self._session.execute(stmt)).scalar_one()
        return int(current) + 1

    async def append(
        self,
        *,
        run_id: uuid.UUID,
        event_type: str,
        message: str,
        level: str = "info",
        payload: dict[str, Any] | None = None,
        screenshot_key: str | None = None,
        attempt_index: int | None = None,
    ) -> RunEvent:
        now = datetime.now(UTC)
        seq = await self.next_seq(run_id)
        row = await self.create(
            run_id=run_id,
            seq=seq,
            ts=now,
            event_type=event_type,
            level=level,
            message=message,
            payload=payload,
            screenshot_key=screenshot_key,
            attempt_index=attempt_index,
        )
        return row

    async def list_since(
        self,
        run_id: uuid.UUID,
        *,
        after_seq: int = 0,
        limit: int = 500,
    ) -> list[RunEvent]:
        stmt = (
            select(RunEvent)
            .where(RunEvent.run_id == run_id, RunEvent.seq > after_seq)
            .order_by(RunEvent.seq.asc())
            .limit(limit)
        )
        return list((await self._session.execute(stmt)).scalars())

    async def max_seq(self, run_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.max(RunEvent.seq), 0)).where(RunEvent.run_id == run_id)
        return int((await self._session.execute(stmt)).scalar_one())
