import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models.account import Account
from app.models.refresh_token import RefreshToken
from app.usecase.logout_usecase import LogoutUseCase


class TestLogoutUseCase:
    async def test_logout_revokes_refresh_token(self, test_session_factory):
        async with test_session_factory() as session:
            account = Account(email="user@example.com")
            session.add(account)
            await session.flush()
            token_raw = secrets.token_urlsafe()
            rt = RefreshToken(
                account_id=account.id,
                token=token_raw,
                expires_at=datetime.now(UTC) + timedelta(days=7),
            )
            session.add(rt)
            await session.commit()

        async with test_session_factory() as session:
            usecase = LogoutUseCase(session)
            await usecase.execute(refresh_token=token_raw)
            await session.commit()

        async with test_session_factory() as session:
            rt = (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.token == token_raw)
                )
            ).scalar_one()
            assert rt.revoked is True

    async def test_logout_does_not_raise_for_nonexistent_token(
        self, test_session_factory
    ):
        async with test_session_factory() as session:
            usecase = LogoutUseCase(session)
            await usecase.execute(refresh_token="nonexistent-token")
