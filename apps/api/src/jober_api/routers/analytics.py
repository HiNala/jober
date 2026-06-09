from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jober_schemas.analytics import AnalyticsBatchRequest
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.context import AuthContext
from jober_api.auth.deps import get_auth_context
from jober_api.db.session import get_session
from jober_api.services.analytics.collector import ingest_client_batch

router = APIRouter(prefix="/events", tags=["analytics"])


async def _optional_auth(request: Request, session: AsyncSession) -> AuthContext | None:
    try:
        return await get_auth_context(request, session)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise


@router.post("", status_code=204)
async def collect_events(
    request: Request,
    body: AnalyticsBatchRequest,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """First-party analytics collector. Always returns 204 (fail silently for clients)."""
    auth = await _optional_auth(request, session)
    await ingest_client_batch(session, request, body, auth)
    return Response(status_code=204)
