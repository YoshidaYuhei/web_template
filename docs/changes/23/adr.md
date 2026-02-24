# ADR: Celery基盤セットアップ + ヘルスチェックジョブ

## 1. 概要

Celery + Redis によるJob基盤を構築し、定期実行バッチの仕組みを導入する。

既存の Docker Compose には Redis サービスが稼働済みであり、これを Celery の Broker として利用する。Worker（タスク実行）と Beat（スケジューラ）を別サービスとして追加し、サンプルとしてヘルスチェックジョブを実装する。

FastAPI アプリケーションとは独立したプロセスとして動作し、既存機能に影響を与えない。

## 2. ファイル構成

```
app/
├── core/
│   └── config.py                              # Celery Broker URL 設定を追加（既存変更）
└── worker/
    ├── __init__.py                            # パッケージ初期化（新規作成）
    ├── celery_app.py                          # Celery アプリ初期化 + スケジュール定義（新規作成）
    └── tasks/
        ├── __init__.py                        # パッケージ初期化（新規作成）
        └── health_check.py                    # ヘルスチェックタスク（新規作成）
tests/
└── worker/
    ├── __init__.py                            # パッケージ初期化（新規作成）
    └── tasks/
        ├── __init__.py                        # パッケージ初期化（新規作成）
        └── test_health_check.py               # ヘルスチェックタスクのテスト（新規作成）
docker-compose.yml                             # worker / beat サービス追加（既存変更）
pyproject.toml                                 # celery[redis] 依存追加（既存変更）
.env.example                                   # 環境変数テンプレート追加（既存変更）
```

## 3. モデリング案

### テーブル定義

新規テーブルの追加はなし。Celery のタスク結果はログのみで管理し、Result Backend は使用しない。

### モデルのライフサイクル

Celery タスクの実行フロー:

1. **Beat がスケジュールを監視**: `celery_app.py` で定義された `beat_schedule` に基づき、実行時刻になったタスクを Redis Broker にエンキューする
2. **Worker がタスクを取得**: Redis からタスクメッセージを dequeue する
3. **タスク実行**: タスク関数を実行し、結果をログに出力する
4. **失敗時リトライ**: 例外発生時は `max_retries` に従いリトライする（デフォルト3回、60秒間隔）

### ビジネスルール

- Beat は常に1プロセスのみ稼働させる（スケジュール重複防止）
- Worker は水平スケール可能（複数プロセス起動可）
- タスクの実行結果は標準出力（ログ）のみに記録する
- タスク失敗時はデフォルト3回までリトライする（指数バックオフなし、60秒固定間隔）
- ヘルスチェックジョブは1分間隔で実行する

## 4. スキーマ設計

API エンドポイントの追加はないため、Request / Response スキーマの新規作成はなし。

## 5. API設計

API エンドポイントの追加はなし。

Celery タスクのインターフェース定義:

### ヘルスチェックタスク

```python
# app/worker/tasks/health_check.py
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def health_check(self) -> dict:
    """
    ヘルスチェックタスク。
    現在時刻とワーカー情報をログに出力する。

    Returns:
        dict: {"status": "ok", "timestamp": "ISO8601文字列", "worker": "ワーカー名"}
    """
```

### Celery Beat スケジュール定義

```python
# app/worker/celery_app.py
celery_app.conf.beat_schedule = {
    "health-check-every-minute": {
        "task": "app.worker.tasks.health_check.health_check",
        "schedule": 60.0,  # 60秒間隔
    },
}
```

### Celery アプリケーション設定

```python
# app/worker/celery_app.py
celery_app = Celery("worker")
celery_app.conf.update(
    broker_url=settings.celery_broker_url,       # redis://redis:6379/0
    result_backend=None,                          # Result Backend 不使用
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    task_track_started=True,
    worker_hijack_root_logger=False,              # 既存ログ設定を維持
)
```

## 6. テストケース一覧

### ヘルスチェックタスクテスト（test_health_check.py）

- タスクが正常に実行され、`{"status": "ok", ...}` を返すこと
- 戻り値に `timestamp` が ISO8601 形式で含まれること
- 戻り値に `worker` キーが含まれること

### Celery アプリケーション設定テスト（test_health_check.py 内）

- `beat_schedule` にヘルスチェックタスクが登録されていること
- ヘルスチェックタスクのスケジュール間隔が 60 秒であること
