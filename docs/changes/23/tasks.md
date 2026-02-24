# タスク: Celery基盤セットアップ + ヘルスチェックジョブ

## 依存パッケージ
- [ ] `pyproject.toml` に `celery[redis]` を dependencies に追加する
- [ ] `uv lock` で lockfile を更新する

## 設定
- [ ] `app/core/config.py` の `Settings` に `redis_host`, `redis_port`, `celery_broker_url` プロパティを追加する
- [ ] `.env.example` に Celery 関連の説明コメントを追加する（既存の REDIS_HOST/REDIS_PORT を利用）

## Celery アプリケーション
- [ ] `app/worker/__init__.py` を作成する
- [ ] `app/worker/tasks/__init__.py` を作成する
- [ ] `app/worker/celery_app.py` を作成する（Celery 初期化 + conf.update + beat_schedule 定義）

## ヘルスチェックジョブ
- [ ] ヘルスチェックタスクのテストコードを追加する（`tests/worker/__init__.py`, `tests/worker/tasks/__init__.py`, `tests/worker/tasks/test_health_check.py`）
  - タスクが正常に実行され `{"status": "ok", ...}` を返すこと
  - 戻り値に `timestamp` が ISO8601 形式で含まれること
  - 戻り値に `worker` キーが含まれること
  - `beat_schedule` にヘルスチェックタスクが登録されていること
  - ヘルスチェックタスクのスケジュール間隔が 60 秒であること
- [ ] `app/worker/tasks/health_check.py` を作成する（ヘルスチェックタスク実装）

## Docker Compose
- [ ] `docker-compose.yml` に `worker` サービスを追加する
- [ ] `docker-compose.yml` に `beat` サービスを追加する

## 完了確認
- [ ] テストを実行し、全て通ること
- [ ] Pull Request を作成して push する
