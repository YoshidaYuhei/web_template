# タスクリスト: ヘルスチェックAPIの強化

## 1. スキーマ作成

- [x] `app/schemas/health.py` を作成
  - [x] `DatabaseHealth` モデルを実装（status, error フィールド）
  - [x] `HealthResponse` モデルを実装（status, database フィールド）

## 2. API構造の準備

- [x] `app/api/v1/internal/__init__.py` を作成（空ファイル）

## 3. ヘルスチェックエンドポイント実装

- [x] `app/api/v1/internal/health.py` を作成
  - [x] `check_database()` 関数を実装（DB接続確認）
  - [x] `health_check()` エンドポイントを実装（GET /health）

## 4. ルーター登録

- [x] `app/api/v1/api.py` を作成
  - [x] `api_router` を作成
  - [x] `health.router` を登録

## 5. main.py の更新

- [x] 既存の `@app.get("/health")` エンドポイントを削除
- [x] `api_router` をインポートして登録

## 6. テスト作成

- [x] `tests/api/v1/internal/test_health.py` を作成
  - [x] 正常時のステータスコード確認（HTTP 200）
  - [x] 正常時のレスポンス構造確認
  - [x] 正常時の status 値確認（"healthy"）
  - [x] 正常時の database.status 確認（"connected"）
  - [x] DB障害時のステータスコード確認（HTTP 503）
  - [x] DB障害時の status 値確認（"unhealthy"）
  - [x] DB障害時の database.status 確認（"disconnected"）
  - [x] DB障害時のエラーメッセージ確認
