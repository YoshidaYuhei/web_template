import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.command.account_command import AccountCommand
from app.core.security import create_access_token, get_password_hash
from app.query.account_query import AccountQuery


@dataclass
class SignupResult:
    account_id: int
    email: str
    is_active: bool
    created_at: datetime
    access_token: str
    refresh_token: str


class SignupUseCase:
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    def __init__(self, session: AsyncSession):
        self._session = session
        self._query = AccountQuery(session)
        self._command = AccountCommand(session)

    async def execute(self, email: str, password: str) -> SignupResult:
        existing = await self._query.get_by_email(email)
        if existing:
            raise ValueError("このメールアドレスは既に登録されています")

        account = await self._command.create_account(email)

        hashed_password = get_password_hash(password)
        await self._command.create_password(account.id, hashed_password)

        refresh_token_raw = secrets.token_urlsafe()
        expires_at = datetime.now(UTC) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        await self._command.create_refresh_token(
            account.id, refresh_token_raw, expires_at
        )

        access_token = create_access_token(data={"sub": str(account.id)})

        return SignupResult(
            account_id=account.id,
            email=account.email,
            is_active=account.is_active,
            created_at=account.created_at,
            access_token=access_token,
            refresh_token=refresh_token_raw,
        )
