from collections.abc import Callable

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.health import DatabaseHealth, HealthResponse

router = APIRouter(tags=["internal"])

# セッションファクトリの型
SessionFactory = Callable[[], AsyncSession]


async def check_database(session_factory: SessionFactory | None = None) -> DatabaseHealth:
    """データベース接続を確認する"""
    if session_factory is None:
        session_factory = AsyncSessionLocal

    try:
        async with session_factory() as session:
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
