import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.command.account_command import AccountCommand
from app.core.security import create_access_token
from app.query.account_query import AccountQuery


@dataclass
class RefreshResult:
    access_token: str
    refresh_token: str


class RefreshUseCase:
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    def __init__(self, session: AsyncSession):
        self._session = session
        self._query = AccountQuery(session)
        self._command = AccountCommand(session)

    async def execute(self, refresh_token: str) -> RefreshResult:
        token_record = await self._query.get_refresh_token(refresh_token)
        if not token_record:
            raise ValueError("無効なリフレッシュトークンです")

        if token_record.revoked:
            raise ValueError("無効なリフレッシュトークンです")

        if token_record.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            raise ValueError("リフレッシュトークンの有効期限が切れています")

        # リフレッシュトークンローテーション: 旧トークンをrevoke
        await self._command.revoke_refresh_token(token_record)

        # 新しいリフレッシュトークンを発行
        new_refresh_token_raw = secrets.token_urlsafe()
        expires_at = datetime.now(UTC) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        await self._command.create_refresh_token(
            token_record.account_id, new_refresh_token_raw, expires_at
        )

        access_token = create_access_token(data={"sub": str(token_record.account_id)})

        return RefreshResult(
            access_token=access_token,
            refresh_token=new_refresh_token_raw,
        )
