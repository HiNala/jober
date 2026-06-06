from jober_schemas.common import SchemaBase


class ImportWarningRead(SchemaBase):
    sheet: str
    row: int | None
    code: str
    message: str


class EntityImportStatsRead(SchemaBase):
    created: int
    updated: int
    skipped: int


class ColumnMappingPreview(SchemaBase):
    field: str
    matched_header: str | None
    confidence: float
    required: bool


class ImportReportRead(SchemaBase):
    import_id: str
    dry_run: bool
    mappings: dict[str, list[ColumnMappingPreview]]
    metadata_sheets: list[str]
    job_targets: EntityImportStatsRead
    company_boards: EntityImportStatsRead
    cover_letter_angles: EntityImportStatsRead
    warnings: list[ImportWarningRead]
