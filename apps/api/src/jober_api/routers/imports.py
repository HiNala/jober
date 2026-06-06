from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import get_session
from jober_api.services.xlsx.import_service import import_jobs_workbook

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/jobs-xlsx")
async def import_jobs_xlsx(
    file: UploadFile = File(...),
    dry_run: bool = Query(False),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    data = await file.read()
    report = await import_jobs_workbook(session, data, dry_run=dry_run)
    return report.as_dict()
