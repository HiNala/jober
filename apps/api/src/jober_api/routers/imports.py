from zipfile import BadZipFile

from fastapi import Depends, File, HTTPException, Query, Request, UploadFile, status
from openpyxl.utils.exceptions import InvalidFileException
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.services.xlsx.import_service import import_jobs_workbook

router = RBACRouter(permission=Permission.AUTHENTICATED, prefix="/imports", tags=["imports"])


@router.post("/jobs-xlsx")
async def import_jobs_xlsx(
    request: Request,
    file: UploadFile = File(...),
    dry_run: bool = Query(False),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload is empty — choose an .xlsx workbook",
        )
    try:
        report = await import_jobs_workbook(
            session,
            data,
            tenant_id=auth.tenant_id,
            dry_run=dry_run,
        )
    except (BadZipFile, InvalidFileException, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not read workbook",
        ) from exc
    return report.as_dict()
