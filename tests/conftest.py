import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token
from app.db.base import Base
from tests.factories import AccountFactory, UserFactory

# テスト用DB設定（同じコンテナ内の別DB）
TEST_DATABASE_URL = "mysql+aiomysql://warry:warry_password@localhost:3306/warry_about_test"

# 無効なDB設定（異常系テスト用）
INVALID_DATABASE_URL = "mysql+aiomysql://invalid:invalid@localhost:9999/invalid"


@pytest.fixture
async def test_engine():
    """テスト用エンジン（テーブル自動作成・削除）"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    """テスト用セッションファクトリ"""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield session_factory


@pytest.fixture
async def test_session(test_session_factory):
    """テスト用セッション"""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


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
    """テスト用HTTPクライアント"""
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


@pytest.fixture
async def test_account(test_session: AsyncSession):
    """ファクトリで作成したテスト用アカウント"""
    account = AccountFactory()
    test_session.add(account)
    await test_session.flush()
    await test_session.refresh(account)
    return account


@pytest.fixture
async def test_user(test_session: AsyncSession, test_account):
    """ファクトリで作成したテスト用ユーザー"""
    user = UserFactory(account_id=test_account.id)
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_account) -> dict[str, str]:
    """認証ヘッダー"""
    access_token = create_access_token(data={"sub": test_account.id})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def authenticated_client(test_session_factory):
    """認証済みユーザー付きのテスト用HTTPクライアント"""
    from app.db.session import get_db
    from app.main import app

    # ユーザーをファクトリで作成してDBに保存
    async with test_session_factory() as session:
        account = AccountFactory()
        session.add(account)
        await session.flush()
        await session.refresh(account)

        user = UserFactory(account_id=account.id)
        session.add(user)
        await session.flush()
        await session.commit()

        # アクセストークンを生成
        access_token = create_access_token(data={"sub": account.id})
        refresh_token = account.refresh_token

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
        # clientと認証情報を一緒に返す
        ac.auth_headers = {"Authorization": f"Bearer {access_token}"}
        ac.access_token = access_token
        ac.refresh_token = refresh_token
        ac.account = account
        ac.user = user
        yield ac

    app.dependency_overrides.clear()
