import uuid


def resume_key(asset_id: uuid.UUID, filename: str) -> str:
    return f"resumes/{asset_id}/{filename}"


def document_pdf_key(job_target_id: uuid.UUID, document_id: uuid.UUID) -> str:
    return f"documents/{job_target_id}/{document_id}.pdf"


def document_docx_key(job_target_id: uuid.UUID, document_id: uuid.UUID) -> str:
    return f"documents/{job_target_id}/{document_id}.docx"


def run_attempt_trace_key(run_id: uuid.UUID, attempt_index: int) -> str:
    return f"runs/{run_id}/attempts/{attempt_index}/trace.zip"


def run_attempt_video_key(run_id: uuid.UUID, attempt_index: int) -> str:
    return f"runs/{run_id}/attempts/{attempt_index}/video.webm"


def run_attempt_screenshot_key(run_id: uuid.UUID, attempt_index: int) -> str:
    return f"runs/{run_id}/attempts/{attempt_index}/screenshot.png"


def run_attempt_dom_key(run_id: uuid.UUID, attempt_index: int) -> str:
    return f"runs/{run_id}/attempts/{attempt_index}/dom.json"
