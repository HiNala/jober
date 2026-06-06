import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.base import Base


class Repository[ModelT: Base]:
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def get(self, entity_id: uuid.UUID) -> ModelT | None:
        return await self._session.get(self._model, entity_id)

    async def create(self, **fields: object) -> ModelT:
        instance = self._model(**fields)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self._session.delete(instance)
        await self._session.flush()

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        stmt = select(self._model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
