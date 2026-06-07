from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.field_mapping_memory import FieldMappingMemory
from jober_api.repositories.base import Repository
from jober_forms.memory import normalize_label


class FieldMappingMemoryRepository(Repository[FieldMappingMemory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FieldMappingMemory)

    async def lookup(self, platform: str, label: str) -> str | None:
        stmt = select(FieldMappingMemory).where(
            FieldMappingMemory.platform == platform.casefold(),
            FieldMappingMemory.label_normalized == normalize_label(label),
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row.mapped_profile_field if row else None

    async def remember(self, platform: str, label: str, mapped_profile_field: str) -> None:
        existing = await self.lookup(platform, label)
        if existing == mapped_profile_field:
            return
        stmt = select(FieldMappingMemory).where(
            FieldMappingMemory.platform == platform.casefold(),
            FieldMappingMemory.label_normalized == normalize_label(label),
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row:
            row.mapped_profile_field = mapped_profile_field
        else:
            await self.create(
                platform=platform.casefold(),
                label_normalized=normalize_label(label),
                mapped_profile_field=mapped_profile_field,
            )
        await self._session.flush()
