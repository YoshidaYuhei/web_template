import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# テスト用DB設定（同じコンテナ内の別DB）
TEST_DATABASE_URL = "mysql+aiomysql://warry:warry_password@localhost:3306/warry_about_test"

# 無効なDB設定（異常系テスト用）
INVALID_DATABASE_URL = "mysql+aiomysql://invalid:invalid@localhost:9999/invalid"


@pytest.fixture
async def test_session_factory():
    """テスト用セッションファクトリ"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield session_factory
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
async def client():
    """テスト用HTTPクライアント"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
