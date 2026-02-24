# 要件定義: Celery基盤セットアップ + ヘルスチェックジョブ

## Why（なぜ必要か）

現在のプロジェクトにはバッチ処理やジョブスケジューラの仕組みが一切存在しない。将来的にデータ集計、通知送信、期限切れトークンの削除などの定期実行タスクが必要になるため、汎用的なJob基盤を先行して構築する。Celery + Redis の組み合わせは Python エコシステムで最も実績があり、既に Docker Compose に Redis が存在するため追加コストが低い。

## UX（ユーザー体験）

本 Issue はインフラ/バックエンド基盤であり、エンドユーザーが直接操作する画面は存在しない。開発者向けの体験として:

- `docker compose up` するだけで Worker / Beat が自動起動する
- ヘルスチェックジョブのログが標準出力に流れ、基盤が動作していることを確認できる
- 新しいジョブを追加する際は、タスク関数を定義してスケジュールに登録するだけで済む

## Issue（解決したい課題）

- 定期実行タスクを実行する仕組みがなく、将来的なバッチ処理要件に対応できない
- cron 等の OS レベルのスケジューラでは、アプリケーションのコンテキスト（DB接続、設定値）との統合が煩雑
- ECS Fargate 環境では cron が使えないため、アプリケーションレベルのスケジューラが必要

## UseCase（ユースケース）

- 開発者が `docker compose up` を実行すると、Worker と Beat が自動的に起動する
- Beat がスケジュールに従ってヘルスチェックタスクを Worker に送信する
- Worker がタスクを受け取り、実行結果をログに出力する
- 開発者が新しい定期実行タスクを追加する際、タスク関数とスケジュール定義のみで完結する
- 既存の FastAPI アプリケーションは影響を受けず、これまで通り動作する

## SpecDelta（既存仕様との差分）

### 新規追加

**パッケージ**
- `celery[redis]` - タスクキュー + Redis ブローカー

**ファイル**
- `app/worker/celery_app.py` - Celery アプリケーション初期化・スケジュール定義
- `app/worker/tasks/health_check.py` - ヘルスチェックタスク
- `app/worker/__init__.py` / `app/worker/tasks/__init__.py` - パッケージ初期化

**Docker Compose サービス**
- `worker` - Celery Worker プロセス
- `beat` - Celery Beat スケジューラプロセス

### 既存変更

- `pyproject.toml` - `celery[redis]` を dependencies に追加
- `app/core/config.py` - Redis URL (Celery Broker用) の設定を追加
- `.env.example` - Celery 関連の環境変数テンプレート追加

### 既存利用（変更なし）

- `redis` サービス（Docker Compose、既存）
- `Dockerfile`（Worker / Beat は同じイメージを使用）
- `.env.development` の `REDIS_HOST` / `REDIS_PORT`（既存）
