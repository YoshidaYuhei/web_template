from datetime import datetime

from pydantic import BaseModel, EmailStr


class AccountCreateRequest(BaseModel):
    """アカウント作成リクエスト（パスワード認証）"""

    email: EmailStr
    password: str


class AccountOauthCreateRequest(BaseModel):
    """OAuth認証情報の追加リクエスト"""

    provider: str
    provider_id: str


class AccountPasskeyCreateRequest(BaseModel):
    """パスキー登録リクエスト"""

    credential_id: str
    public_key: str
    sign_count: int = 0
    transports: str | None = None
    aaguid: str | None = None
    name: str | None = None


class AccountResponse(BaseModel):
    """アカウントレスポンス"""

    id: int
    email: str
    is_active: bool
    has_password: bool
    oauth_providers: list[str]
    passkey_count: int
    created_at: datetime


class AccountOauthResponse(BaseModel):
    """OAuth連携情報レスポンス"""

    id: int
    provider: str
    provider_id: str
    created_at: datetime


class AccountPasskeyResponse(BaseModel):
    """パスキー情報レスポンス"""

    id: int
    credential_id: str
    name: str | None
    transports: str | None
    aaguid: str | None
    created_at: datetime
