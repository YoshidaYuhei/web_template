import pytest
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.account_password import AccountPassword


@pytest.mark.asyncio
class TestAccountPassword:
    async def test_create_account_password(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="pw@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            pw = AccountPassword(account_id=account.id, hashed_password="hashed_xxx")
            session.add(pw)
            await session.commit()
            await session.refresh(pw)

            assert pw.id is not None
            assert pw.account_id == account.id
            assert pw.hashed_password == "hashed_xxx"

            await session.delete(pw)
            await session.delete(account)
            await session.commit()

    async def test_account_id_unique_constraint(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="pw_dup@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            pw1 = AccountPassword(account_id=account.id, hashed_password="hash1")
            session.add(pw1)
            await session.commit()

            pw2 = AccountPassword(account_id=account.id, hashed_password="hash2")
            session.add(pw2)
            pw1_id = pw1.id
            account_id = account.id

            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

            result = await session.get(AccountPassword, pw1_id)
            if result:
                await session.delete(result)
            result_account = await session.get(Account, account_id)
            if result_account:
                await session.delete(result_account)
            await session.commit()
