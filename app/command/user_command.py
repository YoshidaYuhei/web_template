from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Gender, User


class UserCommand:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        account_id: str,
        nickname: str,
        gender: Gender,
        birth_date: date,
    ) -> User:
        user = User(
            account_id=account_id,
            nickname=nickname,
            gender=gender,
            birth_date=birth_date,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
