from uuid import UUID

from jober_schemas.common import TimestampedSchema


class ResumeAssetRead(TimestampedSchema):
    original_filename: str
    is_active: bool
    embedding_id: str | None
    skills: list[str]
    extracted_text_preview: str
    has_text: bool
