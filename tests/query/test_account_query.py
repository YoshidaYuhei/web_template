import pytest

from app.models.account import Account
from app.models.account_oauth import AccountOauth
from app.models.account_passkey import AccountPasskey
from app.models.account_password import AccountPassword
from app.query.account_query import AccountQuery


@pytest.mark.asyncio
class TestAccountQuery:
    async def test_get_by_id(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="q_id@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            query = AccountQuery(session)
            result = await query.get_by_id(account.id)

            assert result is not None
            assert result.id == account.id
            assert result.email == "q_id@example.com"

            await session.delete(account)
            await session.commit()

    async def test_get_by_email(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="q_email@example.com")
            session.add(account)
            await session.commit()

            query = AccountQuery(session)
            result = await query.get_by_email("q_email@example.com")

            assert result is not None
            assert result.email == "q_email@example.com"

            await session.delete(account)
            await session.commit()

    async def test_get_not_found(self, test_session_factory):
        async with test_session_factory() as session:
            query = AccountQuery(session)
            result = await query.get_by_id(999999)

            assert result is None

    async def test_get_with_auth_methods(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="q_auth@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            pw = AccountPassword(account_id=account.id, hashed_password="hash")
            oauth = AccountOauth(
                account_id=account.id, provider="google", provider_id="g_1"
            )
            passkey = AccountPasskey(
                account_id=account.id, credential_id="cred_1", public_key="pk_1"
            )
            session.add_all([pw, oauth, passkey])
            await session.commit()

            query = AccountQuery(session)
            result = await query.get_with_auth_methods(account.id)

            assert result is not None
            assert result.password is not None
            assert len(result.oauths) == 1
            assert len(result.passkeys) == 1

            await session.delete(account)
            await session.commit()
