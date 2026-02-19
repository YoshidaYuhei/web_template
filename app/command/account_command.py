from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.account_oauth import AccountOauth
from app.models.account_passkey import AccountPasskey
from app.models.account_password import AccountPassword
from app.models.refresh_token import RefreshToken


class AccountCommand:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_account(self, email: str) -> Account:
        account = Account(email=email)
        self._session.add(account)
        await self._session.flush()
        return account

    async def create_password(
        self, account_id: int, hashed_password: str
    ) -> AccountPassword:
        pw = AccountPassword(account_id=account_id, hashed_password=hashed_password)
        self._session.add(pw)
        await self._session.flush()
        return pw

    async def create_oauth(
        self, account_id: int, provider: str, provider_id: str
    ) -> AccountOauth:
        oauth = AccountOauth(
            account_id=account_id, provider=provider, provider_id=provider_id
        )
        self._session.add(oauth)
        await self._session.flush()
        return oauth

    async def create_passkey(
        self,
        account_id: int,
        credential_id: str,
        public_key: str,
        sign_count: int = 0,
        transports: str | None = None,
        aaguid: str | None = None,
        name: str | None = None,
    ) -> AccountPasskey:
        passkey = AccountPasskey(
            account_id=account_id,
            credential_id=credential_id,
            public_key=public_key,
            sign_count=sign_count,
            transports=transports,
            aaguid=aaguid,
            name=name,
        )
        self._session.add(passkey)
        await self._session.flush()
        return passkey

    async def create_refresh_token(
        self, account_id: int, token: str, expires_at: datetime
    ) -> RefreshToken:
        rt = RefreshToken(account_id=account_id, token=token, expires_at=expires_at)
        self._session.add(rt)
        await self._session.flush()
        return rt

    async def revoke_refresh_token(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked = True
        await self._session.flush()
