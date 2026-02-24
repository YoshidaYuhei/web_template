from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.account import Account
from app.models.refresh_token import RefreshToken


class AccountQuery:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, account_id: int) -> Account | None:
        result = await self._session.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Account | None:
        result = await self._session.execute(
            select(Account).where(Account.email == email)
        )
        return result.scalar_one_or_none()

    async def get_with_password(self, account_id: int) -> Account | None:
        result = await self._session.execute(
            select(Account)
            .where(Account.id == account_id)
            .options(selectinload(Account.password))
        )
        return result.scalar_one_or_none()

    async def get_with_auth_methods(self, account_id: int) -> Account | None:
        result = await self._session.execute(
            select(Account)
            .where(Account.id == account_id)
            .options(
                selectinload(Account.password),
                selectinload(Account.oauths),
                selectinload(Account.passkeys),
            )
        )
        return result.scalar_one_or_none()

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()
