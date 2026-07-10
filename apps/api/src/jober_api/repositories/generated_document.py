import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import DocumentType
from jober_api.models.generated_document import GeneratedDocument
from jober_api.repositories.base import Repository


class GeneratedDocumentRepository(Repository[GeneratedDocument]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GeneratedDocument)

    async def find_cached_cover_letter(
        self,
        job_target_id: uuid.UUID,
        resume_asset_id: uuid.UUID,
    ) -> GeneratedDocument | None:
        stmt = (
            select(GeneratedDocument)
            .where(
                GeneratedDocument.job_target_id == job_target_id,
                GeneratedDocument.document_type == DocumentType.COVER_LETTER,
            )
            .order_by(GeneratedDocument.generated_at.desc().nulls_last())
        )
        result = await self._session.execute(stmt)
        for row in result.scalars().all():
            meta = row.keyword_coverage or {}
            if meta.get("resume_asset_id") == str(resume_asset_id):
                return row
        return None

    async def find_cached_resume_variant(
        self,
        job_target_id: uuid.UUID,
        resume_asset_id: uuid.UUID,
    ) -> GeneratedDocument | None:
        stmt = (
            select(GeneratedDocument)
            .where(
                GeneratedDocument.job_target_id == job_target_id,
                GeneratedDocument.document_type == DocumentType.RESUME_VARIANT,
            )
            .order_by(GeneratedDocument.generated_at.desc().nulls_last())
        )
        result = await self._session.execute(stmt)
        for row in result.scalars().all():
            meta = row.keyword_coverage or {}
            if meta.get("resume_asset_id") == str(resume_asset_id):
                return row
        return None

    async def list_for_job(
        self,
        job_target_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GeneratedDocument]:
        stmt = (
            select(GeneratedDocument)
            .where(GeneratedDocument.job_target_id == job_target_id)
            .order_by(GeneratedDocument.generated_at.desc().nulls_last())
            .limit(min(limit, 200))
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
