from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import get_session
from jober_api.services.xlsx.export_service import export_jobs_workbook

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/jobs-xlsx")
async def export_jobs_xlsx(
    session: AsyncSession = Depends(get_session),
) -> Response:
    payload = await export_jobs_workbook(session)
    return Response(
        content=payload,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="jober-jobs.xlsx"'},
    )
