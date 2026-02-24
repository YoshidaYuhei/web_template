import secrets
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models.account import Account
from app.models.refresh_token import RefreshToken
from app.usecase.refresh_usecase import RefreshUseCase


async def _create_account_with_refresh_token(
    session, *, days=7, revoked=False
):
    account = Account(email="user@example.com")
    session.add(account)
    await session.flush()
    token_raw = secrets.token_urlsafe()
    rt = RefreshToken(
        account_id=account.id,
        token=token_raw,
        expires_at=datetime.now(UTC) + timedelta(days=days),
        revoked=revoked,
    )
    session.add(rt)
    await session.flush()
    return account, token_raw


class TestRefreshUseCase:
    async def test_refresh_returns_new_tokens(self, test_session_factory):
        async with test_session_factory() as session:
            _account, token_raw = await _create_account_with_refresh_token(session)
            await session.commit()

        async with test_session_factory() as session:
            usecase = RefreshUseCase(session)
            result = await usecase.execute(refresh_token=token_raw)
            await session.commit()

        assert result.access_token
        assert result.refresh_token
        assert result.refresh_token != token_raw

    async def test_refresh_revokes_old_token(self, test_session_factory):
        async with test_session_factory() as session:
            _account, token_raw = await _create_account_with_refresh_token(session)
            await session.commit()

        async with test_session_factory() as session:
            usecase = RefreshUseCase(session)
            await usecase.execute(refresh_token=token_raw)
            await session.commit()

        async with test_session_factory() as session:
            old_rt = (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.token == token_raw)
                )
            ).scalar_one()
            assert old_rt.revoked is True

    async def test_refresh_raises_error_for_invalid_token(self, test_session_factory):
        async with test_session_factory() as session:
            usecase = RefreshUseCase(session)
            with pytest.raises(ValueError, match="無効なリフレッシュトークンです"):
                await usecase.execute(refresh_token="nonexistent-token")

    async def test_refresh_raises_error_for_revoked_token(self, test_session_factory):
        async with test_session_factory() as session:
            _account, token_raw = await _create_account_with_refresh_token(
                session, revoked=True
            )
            await session.commit()

        async with test_session_factory() as session:
            usecase = RefreshUseCase(session)
            with pytest.raises(ValueError, match="無効なリフレッシュトークンです"):
                await usecase.execute(refresh_token=token_raw)

    async def test_refresh_raises_error_for_expired_token(self, test_session_factory):
        async with test_session_factory() as session:
            _account, token_raw = await _create_account_with_refresh_token(
                session, days=-1
            )
            await session.commit()

        async with test_session_factory() as session:
            usecase = RefreshUseCase(session)
            with pytest.raises(
                ValueError, match="リフレッシュトークンの有効期限が切れています"
            ):
                await usecase.execute(refresh_token=token_raw)
