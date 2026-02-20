import os

os.environ["APP_ENV"] = "test"  # config.py の import より前に設定

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()

# 無効なDB設定（異常系テスト用）
INVALID_DATABASE_URL = "postgresql+asyncpg://invalid:invalid@localhost:9999/invalid"


@pytest.fixture
async def test_session_factory():
    """テスト用セッションファクトリ"""
    import app.models  # noqa: F401 — Baseにモデルを登録するために必要

    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield session_factory
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def invalid_session_factory():
    """無効なDB設定のセッションファクトリ（異常系テスト用）"""
    engine = create_async_engine(INVALID_DATABASE_URL)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield session_factory
    await engine.dispose()


@pytest.fixture
async def client(test_session_factory):
    """テスト用HTTPクライアント（テストDB初期化付き）"""
    from app.db.session import get_db
    from app.main import app

    async def override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
