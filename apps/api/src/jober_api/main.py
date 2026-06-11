from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from jober_api.auth.enforcement import bind_route_permissions, validate_rbac_coverage
from jober_api.auth.middleware import AuthMiddleware
from jober_api.config import settings
from jober_api.errors import CorrelationIdMiddleware, register_exception_handlers
from jober_api.health import readiness_report
from jober_api.privacy.logging import configure_logging, init_sentry
from jober_api.privacy.secrets_check import validate_startup_secrets
from jober_api.routers import api_router
from jober_api.services.ops.alerting import dispatch_ops_alerts


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    init_sentry()
    validate_startup_secrets()
    validate_rbac_coverage(_app)
    yield


app = FastAPI(title="Jober API", version="0.1.0", lifespan=lifespan)

app.add_middleware(AuthMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router)
bind_route_permissions(app)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(response: Response) -> dict[str, object]:
    report = await readiness_report(settings.database_url, settings.redis_url)
    if report["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        checks = report.get("checks", {})
        attention = [
            {
                "level": "error",
                "message": f"{name} check failed: {detail.get('detail', 'unknown')}",
            }
            for name, detail in checks.items()
            if isinstance(detail, dict) and not detail.get("ok")
        ]
        if not attention:
            attention = [{"level": "error", "message": "API readiness check failed."}]
        await dispatch_ops_alerts("readyz", attention)
    return report
