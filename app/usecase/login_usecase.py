import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.command.account_command import AccountCommand
from app.core.security import create_access_token, verify_password
from app.query.account_query import AccountQuery


@dataclass
class LoginResult:
    account_id: int
    email: str
    is_active: bool
    created_at: datetime
    access_token: str
    refresh_token: str


class LoginUseCase:
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    def __init__(self, session: AsyncSession):
        self._session = session
        self._query = AccountQuery(session)
        self._command = AccountCommand(session)

    async def execute(self, email: str, password: str) -> LoginResult:
        account = await self._query.get_by_email(email)
        if not account:
            raise ValueError("メールアドレスまたはパスワードが正しくありません")

        account_with_pw = await self._query.get_with_password(account.id)
        if not account_with_pw or not account_with_pw.password:
            raise ValueError("メールアドレスまたはパスワードが正しくありません")

        if not verify_password(password, account_with_pw.password.hashed_password):
            raise ValueError("メールアドレスまたはパスワードが正しくありません")

        if not account.is_active:
            raise ValueError("アカウントが無効です")

        refresh_token_raw = secrets.token_urlsafe()
        expires_at = datetime.now(UTC) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        await self._command.create_refresh_token(
            account.id, refresh_token_raw, expires_at
        )

        access_token = create_access_token(data={"sub": str(account.id)})

        return LoginResult(
            account_id=account.id,
            email=account.email,
            is_active=account.is_active,
            created_at=account.created_at,
            access_token=access_token,
            refresh_token=refresh_token_raw,
        )
