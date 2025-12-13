from pydantic import BaseModel


class DatabaseHealth(BaseModel):
    """データベース接続状態"""

    status: str  # "connected" | "disconnected"
    error: str | None = None


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""

    status: str  # "healthy" | "unhealthy"
    database: DatabaseHealth
