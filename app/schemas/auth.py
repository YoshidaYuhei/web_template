from pydantic import BaseModel

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
