from jober_worker.celery_app import celery_app


@celery_app.task(name="jober_worker.tasks.ping")
def ping() -> str:
    return "pong"
