# 設計書: ヘルスチェックAPIの強化

## 1. 概要

`/health` エンドポイントを強化し、Pydanticスキーマによる型安全なレスポンスとデータベース接続確認機能を追加する。

## 2. ファイル構成

architect.md のディレクトリ構造に準拠：

```
app/
├── schemas/
│   └── health.py              # 新規: ヘルスチェック用スキーマ
├── api/
│   └── v1/
│       ├── api.py             # 変更: internal ルーター登録
│       └── internal/
│           ├── __init__.py    # 新規
│           └── health.py      # 新規: ヘルスチェックエンドポイント
└── main.py                    # 変更: 既存エンドポイント削除、v1ルーター登録

tests/
└── api/
    └── v1/
        └── internal/
            └── test_health.py # 新規: ヘルスチェックテスト
```

## 3. スキーマ設計

### `app/schemas/health.py`

```python
from pydantic import BaseModel


class DatabaseHealth(BaseModel):
    """データベース接続状態"""
    status: str  # "connected" | "disconnected"
    error: str | None = None


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str  # "healthy" | "unhealthy"
    database: DatabaseHealth
```

## 4. API設計

### `app/api/v1/internal/health.py`

```python
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.schemas.health import DatabaseHealth, HealthResponse

router = APIRouter(tags=["internal"])


async def check_database() -> DatabaseHealth:
    """データベース接続を確認する"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return DatabaseHealth(status="connected")
    except Exception as e:
        return DatabaseHealth(status="disconnected", error=str(e))


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {"description": "アプリケーションは正常"},
        503: {"description": "アプリケーションは異常"},
    },
)
async def health_check() -> JSONResponse:
    """
    アプリケーションのヘルスチェックを実行する。

    データベース接続を確認し、結果を返す。
    """
    database = await check_database()

    is_healthy = database.status == "connected"

    response = HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        database=database,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=response.model_dump(),
    )
```

### `app/api/v1/api.py`

```python
from fastapi import APIRouter

from app.api.v1.internal import health

api_router = APIRouter()

# Internal endpoints
api_router.include_router(health.router)
```

## 5. main.py の変更

### 変更前

```python
@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}
```

### 変更後

```python
from app.api.v1.api import api_router

# 既存の @app.get("/health") を削除

app.include_router(api_router)
```

## 6. レスポンス例

### 正常時 (HTTP 200)

```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "error": null
  }
}
```

### 異常時 (HTTP 503)

```json
{
  "status": "unhealthy",
  "database": {
    "status": "disconnected",
    "error": "Connection refused"
  }
}
```

## 7. 実装順序

1. `app/schemas/health.py` を作成
2. `app/api/v1/internal/__init__.py` を作成
3. `app/api/v1/internal/health.py` を作成
4. `app/api/v1/api.py` を作成
5. `app/main.py` を更新（既存エンドポイント削除、v1ルーター登録）
6. `tests/api/v1/internal/test_health.py` を作成

## 8. テストケース一覧

### テストファイル: `tests/api/v1/internal/test_health.py`

| # | テストケース | 目的 |
|---|-------------|------|
| 1 | 正常時のステータスコード確認 | DB接続成功時に HTTP 200 が返ることを確認 |
| 2 | 正常時のレスポンス構造確認 | レスポンスに必須フィールドが含まれることを確認 |
| 3 | 正常時の status 値確認 | `status` が "healthy" であることを確認 |
| 4 | 正常時の database.status 確認 | `database.status` が "connected" であることを確認 |
| 5 | DB障害時のステータスコード確認 | DB接続失敗時に HTTP 503 が返ることを確認 |
| 6 | DB障害時の status 値確認 | `status` が "unhealthy" であることを確認 |
| 7 | DB障害時の database.status 確認 | `database.status` が "disconnected" であることを確認 |
| 8 | DB障害時のエラーメッセージ確認 | `database.error` にエラー内容が含まれることを確認 |
