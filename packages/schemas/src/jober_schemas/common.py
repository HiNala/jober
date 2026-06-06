from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class TimestampedSchema(SchemaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
