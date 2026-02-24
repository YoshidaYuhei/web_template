from pydantic import BaseModel, EmailStr, Field

from app.schemas.account import AccountResponse


class TokenResponse(BaseModel):
    """トークンレスポンス"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SignupResponse(BaseModel):
    """サインアップレスポンス"""

    account: AccountResponse
    token: TokenResponse


class LoginRequest(BaseModel):
    """ログインリクエスト"""

    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """トークンリフレッシュリクエスト"""

    refresh_token: str


LoginResponse = SignupResponse
