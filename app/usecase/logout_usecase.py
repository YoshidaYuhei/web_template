from sqlalchemy.ext.asyncio import AsyncSession

from app.command.account_command import AccountCommand
from app.query.account_query import AccountQuery


class LogoutUseCase:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._query = AccountQuery(session)
        self._command = AccountCommand(session)

    async def execute(self, refresh_token: str) -> None:
        token_record = await self._query.get_refresh_token(refresh_token)
        if token_record and not token_record.revoked:
            await self._command.revoke_refresh_token(token_record)
