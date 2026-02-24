from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("worker")

celery_app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=None,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    task_track_started=True,
    worker_hijack_root_logger=False,
)

celery_app.autodiscover_tasks(["app.worker.tasks"])

celery_app.conf.beat_schedule = {
    "health-check-every-minute": {
        "task": "app.worker.tasks.health_check.health_check",
        "schedule": 60.0,
    },
}
