import pytest
from sqlalchemy import select

from app.core.security import verify_password
from app.models.account import Account
from app.models.account_password import AccountPassword
from app.models.refresh_token import RefreshToken
from app.usecase.signup_usecase import SignupUseCase


class TestSignupUseCase:
    async def test_signup_creates_account_and_password_and_refresh_token(
        self, test_session_factory
    ):
        async with test_session_factory() as session:
            usecase = SignupUseCase(session)
            await usecase.execute(email="user@example.com", password="mypassword1")
            await session.commit()

        async with test_session_factory() as session:
            account = (
                await session.execute(
                    select(Account).where(Account.email == "user@example.com")
                )
            ).scalar_one()
            assert account is not None

            password = (
                await session.execute(
                    select(AccountPassword).where(
                        AccountPassword.account_id == account.id
                    )
                )
            ).scalar_one()
            assert password is not None

            refresh_token = (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.account_id == account.id)
                )
            ).scalar_one()
            assert refresh_token is not None

    async def test_signup_returns_access_token_and_refresh_token(
        self, test_session_factory
    ):
        async with test_session_factory() as session:
            usecase = SignupUseCase(session)
            result = await usecase.execute(
                email="user@example.com", password="mypassword1"
            )

        assert result.access_token
        assert result.refresh_token

    async def test_signup_hashes_password_with_bcrypt(self, test_session_factory):
        async with test_session_factory() as session:
            usecase = SignupUseCase(session)
            await usecase.execute(email="user@example.com", password="mypassword1")
            await session.commit()

        async with test_session_factory() as session:
            account = (
                await session.execute(
                    select(Account).where(Account.email == "user@example.com")
                )
            ).scalar_one()
            password = (
                await session.execute(
                    select(AccountPassword).where(
                        AccountPassword.account_id == account.id
                    )
                )
            ).scalar_one()
            assert verify_password("mypassword1", password.hashed_password)

    async def test_signup_raises_error_for_duplicate_email(self, test_session_factory):
        async with test_session_factory() as session:
            usecase = SignupUseCase(session)
            await usecase.execute(email="dup@example.com", password="mypassword1")
            await session.commit()

        async with test_session_factory() as session:
            usecase = SignupUseCase(session)
            with pytest.raises(
                ValueError, match="このメールアドレスは既に登録されています"
            ):
                await usecase.execute(email="dup@example.com", password="mypassword1")
