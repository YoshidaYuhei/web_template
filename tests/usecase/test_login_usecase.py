import pytest
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models.account import Account
from app.models.account_password import AccountPassword
from app.models.refresh_token import RefreshToken
from app.usecase.login_usecase import LoginUseCase


async def _create_account(session, email="user@example.com", password="mypassword1"):
    account = Account(email=email)
    session.add(account)
    await session.flush()
    pw = AccountPassword(
        account_id=account.id, hashed_password=get_password_hash(password)
    )
    session.add(pw)
    await session.flush()
    return account


class TestLoginUseCase:
    async def test_login_returns_tokens_for_valid_credentials(
        self, test_session_factory
    ):
        async with test_session_factory() as session:
            await _create_account(session)
            await session.commit()

        async with test_session_factory() as session:
            usecase = LoginUseCase(session)
            result = await usecase.execute(
                email="user@example.com", password="mypassword1"
            )

        assert result.access_token
        assert result.refresh_token
        assert result.email == "user@example.com"

    async def test_login_creates_refresh_token_in_db(self, test_session_factory):
        async with test_session_factory() as session:
            account = await _create_account(session)
            account_id = account.id
            await session.commit()

        async with test_session_factory() as session:
            usecase = LoginUseCase(session)
            await usecase.execute(email="user@example.com", password="mypassword1")
            await session.commit()

        async with test_session_factory() as session:
            rt = (
                await session.execute(
                    select(RefreshToken).where(
                        RefreshToken.account_id == account_id
                    )
                )
            ).scalar_one()
            assert rt is not None
            assert not rt.revoked

    async def test_login_raises_error_for_wrong_password(self, test_session_factory):
        async with test_session_factory() as session:
            await _create_account(session)
            await session.commit()

        async with test_session_factory() as session:
            usecase = LoginUseCase(session)
            with pytest.raises(
                ValueError, match="メールアドレスまたはパスワードが正しくありません"
            ):
                await usecase.execute(
                    email="user@example.com", password="wrongpassword"
                )

    async def test_login_raises_error_for_unregistered_email(
        self, test_session_factory
    ):
        async with test_session_factory() as session:
            usecase = LoginUseCase(session)
            with pytest.raises(
                ValueError, match="メールアドレスまたはパスワードが正しくありません"
            ):
                await usecase.execute(
                    email="nobody@example.com", password="mypassword1"
                )
