from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountCommand:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        email: str,
        hashed_password: str,
        refresh_token: str,
        refresh_token_expires_at: datetime,
    ) -> Account:
        account = Account(
            email=email,
            hashed_password=hashed_password,
            refresh_token=refresh_token,
            refresh_token_expires_at=refresh_token_expires_at,
        )
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def update_refresh_token(
        self,
        account_id: str,
        refresh_token: str,
        expires_at: datetime,
    ) -> None:
        from app.query.account_query import AccountQuery

        query = AccountQuery(self.db)
        account = await query.get_by_id(account_id)
        if account:
            account.refresh_token = refresh_token
            account.refresh_token_expires_at = expires_at
            await self.db.flush()

    async def clear_refresh_token(self, account_id: str) -> None:
        from app.query.account_query import AccountQuery

        query = AccountQuery(self.db)
        account = await query.get_by_id(account_id)
        if account:
            account.refresh_token = None
            account.refresh_token_expires_at = None
            await self.db.flush()
