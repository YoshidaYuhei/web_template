import logging
from datetime import UTC, datetime

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def health_check(self) -> dict:
    """ヘルスチェックタスク。現在時刻とワーカー情報をログに出力する。"""
    now = datetime.now(UTC)
    worker_name = self.request.hostname or "unknown"

    result = {
        "status": "ok",
        "timestamp": now.isoformat(),
        "worker": worker_name,
    }

    logger.info("Health check: %s", result)
    return result
