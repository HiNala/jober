from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.auth.tenant_guard import require_job_for_tenant
from jober_api.db.session import get_session
from jober_api.models.generated_document import GeneratedDocument
from jober_api.repositories.generated_document import GeneratedDocumentRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.documents.cover_letter_generator import (
    ClaimsRejectedError,
    _extraction_context,
    _serialize_document,
    duplicate_cover_letter,
    generate_cover_letter,
)
from jober_api.services.documents.letter_editor import persist_letter_text
from jober_api.services.documents.letter_styles import LETTER_TEMPLATES, VOICE_PRESETS
from jober_api.services.llm.gateway import BudgetExceededError
from jober_api.storage.minio_client import ObjectStorage

router = RBACRouter(permission=Permission.AUTHENTICATED, prefix="/documents", tags=["documents"])


def get_storage() -> ObjectStorage:
    return ObjectStorage()


async def _document_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    document_id: uuid.UUID,
) -> GeneratedDocument:
    repo = GeneratedDocumentRepository(session)
    row = await repo.get(document_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await require_job_for_tenant(session, tenant_id, row.job_target_id)
    return row


@router.get("/letter-options")
async def letter_options() -> dict[str, object]:
    return {
        "templates": sorted(LETTER_TEMPLATES),
        "voice_presets": sorted(VOICE_PRESETS),
    }


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

    run_id = uuid.UUID(str(body["run_id"])) if body.get("run_id") else None
    parent_raw = body.get("parent_document_id")
    parent_id = uuid.UUID(str(parent_raw)) if parent_raw else None
    locked = body.get("locked_paragraphs")
    locked_list = [int(str(i)) for i in locked] if isinstance(locked, list) else None
    regen_raw = body.get("regenerate_paragraph_index")
    regen_index = int(str(regen_raw)) if regen_raw is not None else None

    try:
        result = await generate_cover_letter(
            session,
            storage,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            job_target_id=job_target_id,
            force=bool(body.get("force", False)),
            include_docx=bool(body.get("include_docx", True)),
            job_description=str(body.get("job_description") or ""),
            job_requirements=str(body.get("job_requirements") or ""),
            company_summary=str(body.get("company_summary") or ""),
            run_id=run_id,
            template_style=str(body["template_style"]) if body.get("template_style") else None,
            voice_preset=str(body["voice_preset"]) if body.get("voice_preset") else None,
            locked_paragraphs=locked_list,
            regenerate_paragraph_index=regen_index,
            parent_document_id=parent_id,
            seed_text=str(body["seed_text"]) if body.get("seed_text") else None,
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
    await require_job_for_tenant(session, auth.tenant_id, job_target_id)
    repo = GeneratedDocumentRepository(session)
    rows = await repo.list_for_job(job_target_id)
    return {
        "items": [
            {
                "id": str(row.id),
                "document_type": row.document_type.value,
                "ats_score": row.ats_score,
                "generated_at": row.generated_at.isoformat() if row.generated_at else None,
                "version": (row.keyword_coverage or {}).get("version", 1),
                "template_style": (row.keyword_coverage or {}).get("template_style"),
                "voice_preset": (row.keyword_coverage or {}).get("voice_preset"),
            }
            for row in rows
        ]
    }


@router.get("/{document_id}")
async def get_document(
    request: Request,
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    row = await _document_for_tenant(session, auth.tenant_id, document_id)
    return _serialize_document(row, cached=False)


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


@router.patch("/{document_id}")
async def patch_document(
    document_id: uuid.UUID,
    request: Request,
    body: dict[str, object],
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorage = Depends(get_storage),
) -> dict[str, object]:
    auth = require_auth(request)
    row = await _document_for_tenant(session, auth.tenant_id, document_id)
    jobs = JobTargetRepository(session, auth.tenant_id)
    job = await jobs.get(row.job_target_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    meta = dict(row.keyword_coverage or {})
    if "locked_template" in body:
        meta["locked_template"] = bool(body["locked_template"])
        if meta["locked_template"]:
            meta["template_fit_lane"] = job.fit_lane
    if "locked_paragraphs" in body and isinstance(body["locked_paragraphs"], list):
        meta["locked_paragraphs"] = [int(str(i)) for i in body["locked_paragraphs"]]
    if body.get("template_style"):
        meta["template_style"] = str(body["template_style"])
    if body.get("voice_preset"):
        meta["voice_preset"] = str(body["voice_preset"])
    row.keyword_coverage = meta

    if "text" in body and isinstance(body["text"], str):
        profiles = UserProfileRepository(session, auth.tenant_id)
        profile = await profiles.get_singleton()
        applicant = profile.name if profile and profile.name else "Applicant"
        desc, reqs, _ = _extraction_context(job)
        updated = await persist_letter_text(
            storage,
            row=row,
            job=job,
            body=str(body["text"]),
            applicant_name=applicant,
            job_description=desc,
            job_requirements=reqs,
        )
        await session.commit()
        return {"id": str(row.id), **updated, "locked_template": bool(meta.get("locked_template"))}

    await session.commit()
    return {
        "id": str(row.id),
        "locked_template": bool(meta.get("locked_template")),
        "locked_paragraphs": meta.get("locked_paragraphs") or [],
        "template_style": meta.get("template_style"),
        "voice_preset": meta.get("voice_preset"),
    }


@router.post("/{document_id}/duplicate")
async def duplicate_document(
    document_id: uuid.UUID,
    request: Request,
    body: dict[str, object] | None = None,
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorage = Depends(get_storage),
) -> dict[str, object]:
    auth = require_auth(request)
    await _document_for_tenant(session, auth.tenant_id, document_id)
    payload = body or {}
    target_job = uuid.UUID(str(payload["job_target_id"])) if payload.get("job_target_id") else None
    try:
        result = await duplicate_cover_letter(
            session,
            storage,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            document_id=document_id,
            target_job_target_id=target_job,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await session.commit()
    return result


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
