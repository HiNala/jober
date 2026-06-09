
from fastapi import Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.services.xlsx.export_service import export_jobs_workbook

router = RBACRouter(permission=Permission.AUTHENTICATED, prefix="/exports", tags=["exports"])


@router.get("/jobs-xlsx")
async def export_jobs_xlsx(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Response:
    auth = require_auth(request)
    payload = await export_jobs_workbook(session, auth.tenant_id)
    return Response(
        content=payload,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="jober-jobs.xlsx"'},
    )
