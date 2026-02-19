from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.refresh_token import RefreshToken


@pytest.mark.asyncio
class TestRefreshToken:
    async def test_create_refresh_token(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="rt@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            rt = RefreshToken(
                account_id=account.id,
                token="token_abc_123",
                expires_at=datetime(2099, 1, 1, tzinfo=UTC),
            )
            session.add(rt)
            await session.commit()
            await session.refresh(rt)

            assert rt.id is not None
            assert rt.token == "token_abc_123"
            assert rt.account_id == account.id

            await session.delete(rt)
            await session.delete(account)
            await session.commit()

    async def test_token_unique_constraint(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="rt_dup@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            rt1 = RefreshToken(
                account_id=account.id,
                token="dup_token",
                expires_at=datetime(2099, 1, 1, tzinfo=UTC),
            )
            session.add(rt1)
            await session.commit()

            rt2 = RefreshToken(
                account_id=account.id,
                token="dup_token",
                expires_at=datetime(2099, 1, 1, tzinfo=UTC),
            )
            session.add(rt2)
            rt1_id = rt1.id
            account_id = account.id

            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

            result = await session.get(RefreshToken, rt1_id)
            if result:
                await session.delete(result)
            result_account = await session.get(Account, account_id)
            if result_account:
                await session.delete(result_account)
            await session.commit()

    async def test_revoked_default_false(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="rt_rev@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            rt = RefreshToken(
                account_id=account.id,
                token="token_rev_test",
                expires_at=datetime(2099, 1, 1, tzinfo=UTC),
            )
            session.add(rt)
            await session.commit()
            await session.refresh(rt)

            assert rt.revoked is False

            await session.delete(rt)
            await session.delete(account)
            await session.commit()
