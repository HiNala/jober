from __future__ import annotations

import uuid

from jober_worker.celery_app import celery_app
from jober_worker.extraction_runner import run_browser_extraction
from jober_worker.job_context import load_extraction_context


@celery_app.task(name="jober_worker.tasks.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="jober_worker.tasks.extract_job", bind=True)
def extract_job(
    self,
    run_id: str,
    job_target_id: str,
    url: str,
    force: bool = False,
) -> dict[str, object]:
    del self, force
    ctx = load_extraction_context(uuid.UUID(job_target_id))
    return run_browser_extraction(
        run_id=uuid.UUID(run_id),
        job_target_id=uuid.UUID(job_target_id),
        url=url,
        company_hint=str(ctx.get("company_hint", "")),
        resume_skills=ctx.get("resume_skills") or None,
    )
