from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.middleware import require_auth
from jober_api.db.session import get_session
from jober_api.models.generated_document import GeneratedDocument
from jober_api.repositories.generated_document import GeneratedDocumentRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.documents.cover_letter_generator import (
    ClaimsRejectedError,
    generate_cover_letter,
)
from jober_api.services.llm.gateway import BudgetExceededError
from jober_api.storage.minio_client import ObjectStorage

router = APIRouter(prefix="/documents", tags=["documents"])


def get_storage() -> ObjectStorage:
    return ObjectStorage()


async def _require_job_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    job_target_id: uuid.UUID,
) -> None:
    jobs = JobTargetRepository(session, tenant_id)
    if await jobs.get(job_target_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job target not found")


async def _document_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    document_id: uuid.UUID,
) -> GeneratedDocument:
    repo = GeneratedDocumentRepository(session)
    row = await repo.get(document_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await _require_job_for_tenant(session, tenant_id, row.job_target_id)
    return row


@router.post("/generate-cover-letter")
async def generate_cover_letter_endpoint(
    request: Request,
    body: dict[str, object],
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorage = Depends(get_storage),
) -> dict[str, object]:
    auth = require_auth(request)
    raw_id = body.get("job_target_id")
    if not raw_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="job_target_id required",
        )
    try:
        job_target_id = uuid.UUID(str(raw_id))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid UUID",
        ) from exc

    force = bool(body.get("force", False))
    include_docx = bool(body.get("include_docx", True))
    try:
        result = await generate_cover_letter(
            session,
            storage,
            tenant_id=auth.tenant_id,
            job_target_id=job_target_id,
            force=force,
            include_docx=include_docx,
            job_description=str(body.get("job_description") or ""),
            job_requirements=str(body.get("job_requirements") or ""),
            company_summary=str(body.get("company_summary") or ""),
        )
    except BudgetExceededError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc)) from exc
    except ClaimsRejectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Claims guard rejected draft", "unsupported": exc.unsupported},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    await session.commit()
    return result


@router.get("")
async def list_documents(
    request: Request,
    job_target_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await _require_job_for_tenant(session, auth.tenant_id, job_target_id)
    repo = GeneratedDocumentRepository(session)
    rows = await repo.list_for_job(job_target_id)
    return {
        "items": [
            {
                "id": str(row.id),
                "document_type": row.document_type.value,
                "ats_score": row.ats_score,
                "generated_at": row.generated_at.isoformat() if row.generated_at else None,
            }
            for row in rows
        ]
    }


@router.get("/{document_id}/download/pdf")
async def download_pdf(
    request: Request,
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorage = Depends(get_storage),
) -> Response:
    auth = require_auth(request)
    row = await _document_for_tenant(session, auth.tenant_id, document_id)
    if not row.object_key_pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = await storage.get_bytes(row.object_key_pdf)
    return Response(content=data, media_type="application/pdf")


@router.get("/{document_id}/download/docx")
async def download_docx(
    request: Request,
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorage = Depends(get_storage),
) -> Response:
    auth = require_auth(request)
    row = await _document_for_tenant(session, auth.tenant_id, document_id)
    if not row.object_key_docx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = await storage.get_bytes(row.object_key_docx)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
