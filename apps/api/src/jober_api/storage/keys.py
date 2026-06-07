import uuid


def tenant_root(tenant_id: uuid.UUID) -> str:
    return f"tenants/{tenant_id}/"


def resume_key(asset_id: uuid.UUID, filename: str, *, tenant_id: uuid.UUID | None = None) -> str:
    prefix = f"tenants/{tenant_id}/" if tenant_id else ""
    return f"{prefix}resumes/{asset_id}/{filename}"


def document_pdf_key(
    job_target_id: uuid.UUID,
    document_id: uuid.UUID,
    *,
    tenant_id: uuid.UUID | None = None,
) -> str:
    prefix = f"tenants/{tenant_id}/" if tenant_id else ""
    return f"{prefix}documents/{job_target_id}/{document_id}.pdf"


def document_docx_key(
    job_target_id: uuid.UUID,
    document_id: uuid.UUID,
    *,
    tenant_id: uuid.UUID | None = None,
) -> str:
    prefix = f"tenants/{tenant_id}/" if tenant_id else ""
    return f"{prefix}documents/{job_target_id}/{document_id}.docx"


def _run_base(run_id: uuid.UUID, tenant_id: uuid.UUID | None = None) -> str:
    if tenant_id:
        return f"tenants/{tenant_id}/runs/{run_id}"
    return f"runs/{run_id}"


def run_attempt_trace_key(
    run_id: uuid.UUID, attempt_index: int, *, tenant_id: uuid.UUID | None = None
) -> str:
    return f"{_run_base(run_id, tenant_id)}/attempts/{attempt_index}/trace.zip"


def run_attempt_video_key(
    run_id: uuid.UUID, attempt_index: int, *, tenant_id: uuid.UUID | None = None
) -> str:
    return f"{_run_base(run_id, tenant_id)}/attempts/{attempt_index}/video.webm"


def run_attempt_screenshot_key(
    run_id: uuid.UUID, attempt_index: int, *, tenant_id: uuid.UUID | None = None
) -> str:
    return f"{_run_base(run_id, tenant_id)}/attempts/{attempt_index}/screenshot.png"


def run_attempt_dom_key(
    run_id: uuid.UUID, attempt_index: int, *, tenant_id: uuid.UUID | None = None
) -> str:
    return f"{_run_base(run_id, tenant_id)}/attempts/{attempt_index}/dom.json"


def run_storage_state_key(run_id: uuid.UUID, *, tenant_id: uuid.UUID | None = None) -> str:
    return f"{_run_base(run_id, tenant_id)}/storage-state.enc"


def run_prefix(run_id: uuid.UUID, *, tenant_id: uuid.UUID | None = None) -> str:
    return f"{_run_base(run_id, tenant_id)}/"
