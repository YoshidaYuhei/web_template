import pytest
from sqlalchemy.exc import IntegrityError

from app.models.account import Account


@pytest.mark.asyncio
class TestAccount:
    async def test_create_account(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="test@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            assert account.id is not None
            assert account.email == "test@example.com"

            await session.delete(account)
            await session.commit()

    async def test_email_unique_constraint(self, test_session_factory):
        async with test_session_factory() as session:
            account1 = Account(email="dup@example.com")
            session.add(account1)
            await session.commit()

            account2 = Account(email="dup@example.com")
            session.add(account2)
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

            await session.delete(account1)
            await session.commit()

    async def test_is_active_default_true(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="active@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            assert account.is_active is True

            await session.delete(account)
            await session.commit()

    async def test_timestamps_auto_set(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="ts@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            assert account.created_at is not None
            assert account.updated_at is not None

            await session.delete(account)
            await session.commit()
