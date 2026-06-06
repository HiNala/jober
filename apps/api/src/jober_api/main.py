from fastapi import FastAPI, Response, status

from jober_api.config import settings
from jober_api.health import readiness_report

app = FastAPI(title="Jober API", version="0.1.0")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(response: Response) -> dict[str, object]:
    report = await readiness_report(settings.database_url, settings.redis_url)
    if report["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report
