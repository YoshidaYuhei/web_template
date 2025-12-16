from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserQuery:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_account_id(self, account_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.account_id == account_id)
        )
        return result.scalar_one_or_none()
