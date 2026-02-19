import pytest
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.account_oauth import AccountOauth


@pytest.mark.asyncio
class TestAccountOauth:
    async def test_create_account_oauth(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="oauth@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            oauth = AccountOauth(
                account_id=account.id,
                provider="google",
                provider_id="google_123",
            )
            session.add(oauth)
            await session.commit()
            await session.refresh(oauth)

            assert oauth.id is not None
            assert oauth.provider == "google"
            assert oauth.provider_id == "google_123"

            await session.delete(oauth)
            await session.delete(account)
            await session.commit()

    async def test_multiple_providers(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="multi_oauth@example.com")
            session.add(account)
            await session.commit()
            await session.refresh(account)

            oauth_google = AccountOauth(
                account_id=account.id,
                provider="google",
                provider_id="g_456",
            )
            oauth_github = AccountOauth(
                account_id=account.id,
                provider="github",
                provider_id="gh_789",
            )
            session.add_all([oauth_google, oauth_github])
            await session.commit()

            await session.refresh(oauth_google)
            await session.refresh(oauth_github)
            assert oauth_google.id is not None
            assert oauth_github.id is not None

            await session.delete(oauth_google)
            await session.delete(oauth_github)
            await session.delete(account)
            await session.commit()

    async def test_provider_provider_id_unique_constraint(self, test_session_factory):
        async with test_session_factory() as session:
            account1 = Account(email="oauth_dup1@example.com")
            account2 = Account(email="oauth_dup2@example.com")
            session.add_all([account1, account2])
            await session.commit()
            await session.refresh(account1)
            await session.refresh(account2)

            oauth1 = AccountOauth(
                account_id=account1.id,
                provider="google",
                provider_id="same_id",
            )
            session.add(oauth1)
            await session.commit()

            oauth2 = AccountOauth(
                account_id=account2.id,
                provider="google",
                provider_id="same_id",
            )
            session.add(oauth2)
            oauth1_id = oauth1.id
            account1_id = account1.id
            account2_id = account2.id

            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

            result = await session.get(AccountOauth, oauth1_id)
            if result:
                await session.delete(result)
            for acc_id in [account1_id, account2_id]:
                a = await session.get(Account, acc_id)
                if a:
                    await session.delete(a)
            await session.commit()
