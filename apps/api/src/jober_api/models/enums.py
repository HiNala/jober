from enum import StrEnum


class RunStatus(StrEnum):
    QUEUED = "queued"
    PREPARE_CONTEXT = "prepare_context"
    OPEN_JOB = "open_job"
    DETECT_PLATFORM = "detect_platform"
    EXTRACT_JOB = "extract_job"
    GENERATE_DOCUMENTS = "generate_documents"
    DISCOVER_FORM = "discover_form"
    FILL_FORM = "fill_form"
    UPLOAD_FILES = "upload_files"
    VERIFY_READY = "verify_ready"
    NEEDS_HUMAN = "needs_human"
    REVIEW_AND_SUBMIT = "review_and_submit"
    VERIFY_SUBMISSION = "verify_submission"
    SUCCEEDED = "succeeded"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_FINAL = "failed_final"
    SKIPPED = "skipped"


class RunPolicy(StrEnum):
    DRY_RUN = "dry_run"
    REVIEW_BEFORE_SUBMIT = "review_before_submit"
    AUTO_SUBMIT = "auto_submit"


class AttemptStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class FieldObservationStatus(StrEnum):
    FILLED = "filled"
    SKIPPED = "skipped"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class CheckpointType(StrEnum):
    CAPTCHA = "captcha"
    LOGIN = "login"
    TWO_FACTOR = "two_factor"
    REVIEW_SUBMIT = "review_submit"
    SENSITIVE_FIELD = "sensitive_field"
    MANUAL_INTERVENTION = "manual_intervention"


class CheckpointStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class DocumentType(StrEnum):
    COVER_LETTER = "cover_letter"
    RESUME_VARIANT = "resume_variant"


class JobTargetStatus(StrEnum):
    NEW = "new"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    APPLIED = "applied"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    SKIPPED = "skipped"


class BatchStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BatchItemStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
