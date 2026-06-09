from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from jober_api.auth.enforcement import (
    PermissionMiddleware,
    bind_route_permissions,
    validate_rbac_coverage,
)
from jober_api.auth.middleware import AuthMiddleware
from jober_api.config import settings
from jober_api.health import readiness_report
from jober_api.privacy.secrets_check import validate_startup_secrets
from jober_api.routers import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    validate_startup_secrets()
    bind_route_permissions(_app)
    validate_rbac_coverage(_app)
    yield


app = FastAPI(title="Jober API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(PermissionMiddleware)

app.include_router(api_router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(response: Response) -> dict[str, object]:
    report = await readiness_report(settings.database_url, settings.redis_url)
    if report["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report
