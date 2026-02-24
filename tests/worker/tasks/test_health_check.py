from datetime import datetime

import pytest

from app.worker.celery_app import celery_app


@pytest.fixture(autouse=True)
def celery_eager_mode():
    """テスト時はタスクを同期実行する"""
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = False
    celery_app.conf.task_eager_propagates = False


class TestHealthCheckTask:
    """ヘルスチェックタスクのテスト"""

    def test_returns_ok_status(self):
        """タスクが正常に実行され status が ok であること"""
        from app.worker.tasks.health_check import health_check

        result = health_check.apply().get()

        assert result["status"] == "ok"

    def test_returns_iso8601_timestamp(self):
        """戻り値に timestamp が ISO8601 形式で含まれること"""
        from app.worker.tasks.health_check import health_check

        result = health_check.apply().get()

        assert "timestamp" in result
        datetime.fromisoformat(result["timestamp"])

    def test_returns_worker_key(self):
        """戻り値に worker キーが含まれること"""
        from app.worker.tasks.health_check import health_check

        result = health_check.apply().get()

        assert "worker" in result


class TestCeleryBeatSchedule:
    """Celery Beat スケジュール設定のテスト"""

    def test_health_check_task_is_registered(self):
        """beat_schedule にヘルスチェックタスクが登録されていること"""
        schedule = celery_app.conf.beat_schedule

        assert "health-check-every-minute" in schedule
        assert (
            schedule["health-check-every-minute"]["task"]
            == "app.worker.tasks.health_check.health_check"
        )

    def test_health_check_schedule_interval_is_60_seconds(self):
        """ヘルスチェックタスクのスケジュール間隔が 60 秒であること"""
        schedule = celery_app.conf.beat_schedule

        assert schedule["health-check-every-minute"]["schedule"] == 60.0
