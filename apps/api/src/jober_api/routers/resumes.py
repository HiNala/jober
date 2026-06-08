from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.middleware import require_auth
from jober_api.db.session import get_session
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.serializers.profile import serialize_resume
from jober_api.services.resume_service import upload_resume
from jober_api.storage.minio_client import ObjectStorage

router = APIRouter(prefix="/resumes", tags=["resumes"])


def get_storage() -> ObjectStorage:
    return ObjectStorage()


@router.get("")
async def list_resumes(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    repo = ResumeAssetRepository(session, auth.tenant_id)
    rows = await repo.list_all(limit=50)
    return {"items": [serialize_resume(row) for row in rows]}


@router.post("")
async def upload_resume_file(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorage = Depends(get_storage),
) -> dict[str, object]:
    auth = require_auth(request)
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty upload")

    profiles = UserProfileRepository(session, auth.tenant_id)
    profile = await profiles.get_or_create_for_tenant()
    try:
        asset = await upload_resume(
            session,
            storage,
            profile,
            filename=file.filename,
            data=data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    await session.commit()
    return serialize_resume(asset)
