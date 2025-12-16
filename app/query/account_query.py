from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountQuery:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: str) -> Account | None:
        result = await self.db.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Account | None:
        result = await self.db.execute(
            select(Account).where(Account.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_refresh_token(self, refresh_token: str) -> Account | None:
        result = await self.db.execute(
            select(Account).where(Account.refresh_token == refresh_token)
        )
        return result.scalar_one_or_none()
