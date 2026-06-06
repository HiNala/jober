from jober_worker.celery_app import celery_app


# Celery's task decorator lacks upstream stubs (see pyproject mypy overrides).
@celery_app.task(name="jober_worker.tasks.ping")  # type: ignore[untyped-decorator]
def ping() -> str:
    return "pong"
