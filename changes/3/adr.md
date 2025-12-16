# ADR: ログイン機能を追加する

**Issue:** #3
**作成日:** 2025-12-14

---

## 1. 概要

JWT認証 + リフレッシュトークン方式によるログイン機能を実装する。

### 認証フロー

```
[サインアップ/ログイン]
    ↓
[アクセストークン(JWT) + リフレッシュトークン発行]
    ↓
[APIリクエスト時: Authorizationヘッダーにアクセストークン付与]
    ↓
[アクセストークン期限切れ: リフレッシュトークンで更新]
    ↓
[ログアウト: Accountのリフレッシュトークンをクリア]
```

### 設計方針

- **Account/User分離**: 認証情報（Account）とプロフィール情報（User）を1:1で分離
- **リフレッシュトークン**: Accountモデルのフィールドとして保存（1アカウント1セッション）
- **トークンローテーション**: リフレッシュ時に新しいリフレッシュトークンを発行
- **認証ロジック**: エンドポイントから直接 command/query を呼び出す（usecaseレイヤー不使用）

---

## 2. ファイル構成

```
app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── auth.py           # 認証エンドポイント（新規）
│           └── users.py          # ユーザーエンドポイント（新規）
├── core/
│   ├── config.py                 # 設定（修正: refresh_token_expire_days追加）
│   ├── security.py               # セキュリティ（修正: リフレッシュトークン関連追加）
│   └── deps.py                   # 依存関係（新規: get_current_user等）
├── models/
│   ├── __init__.py               # モデルエクスポート（修正）
│   ├── account.py                # Accountモデル（新規）
│   └── user.py                   # Userモデル（新規）
├── schemas/
│   ├── __init__.py               # スキーマエクスポート（修正）
│   ├── auth.py                   # 認証スキーマ（新規）
│   └── user.py                   # ユーザースキーマ（新規）
├── query/
│   ├── account_query.py          # Account読み取りクエリ（新規）
│   └── user_query.py             # User読み取りクエリ（新規）
└── command/
    ├── account_command.py        # Account書き込みコマンド（新規）
    └── user_command.py           # User書き込みコマンド（新規）

alembic/
└── versions/
    └── xxxx_create_account_and_user_tables.py  # マイグレーション（新規）

tests/
├── schemas/
│   └── test_auth_schema.py       # 認証スキーマテスト（新規）
├── api/
│   └── v1/
│       └── endpoints/
│           ├── test_auth.py      # 認証APIテスト（新規）
│           └── test_users.py     # ユーザーAPIテスト（新規）
└── conftest.py                   # テストフィクスチャ（修正）
```

---

## 3. スキーマ設計

### 3.1 Accountテーブル

```sql
CREATE TABLE accounts (
    id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    refresh_token VARCHAR(255) NULL,
    refresh_token_expires_at DATETIME NULL,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_accounts_email (email)
);
```

### 3.2 Usersテーブル

```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    account_id CHAR(36) NOT NULL UNIQUE,
    nickname VARCHAR(100) NOT NULL,
    gender ENUM('male', 'female') NOT NULL,
    birth_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_users_account FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_users_account_id (account_id)
);
```

### 3.3 SQLAlchemyモデル

#### app/models/account.py

```python
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    refresh_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="account", uselist=False)
```

#### app/models/user.py

```python
import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    account_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("accounts.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    account: Mapped["Account"] = relationship("Account", back_populates="user")
```

---

## 4. API設計

### 4.1 エンドポイント一覧

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| POST | /api/v1/auth/signup | 不要 | ユーザー登録 |
| POST | /api/v1/auth/login | 不要 | ログイン |
| POST | /api/v1/auth/logout | 必要 | ログアウト |
| POST | /api/v1/auth/refresh | 不要 | トークンリフレッシュ |
| GET | /api/v1/users/me | 必要 | 現在のユーザー情報取得 |

### 4.2 認証エンドポイント

#### app/api/v1/endpoints/auth.py

```python
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.command.account_command import AccountCommand
from app.command.user_command import UserCommand
from app.core.config import get_settings
from app.core.deps import get_current_account
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)
from app.db.session import get_db
from app.models.account import Account
from app.query.account_query import AccountQuery
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """ユーザー登録"""
    account_query = AccountQuery(db)
    existing = await account_query.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Account作成
    account_command = AccountCommand(db)
    hashed_password = get_password_hash(request.password)
    refresh_token, expires_at = create_refresh_token()

    account = await account_command.create(
        email=request.email,
        hashed_password=hashed_password,
        refresh_token=refresh_token,
        refresh_token_expires_at=expires_at,
    )

    # User作成
    user_command = UserCommand(db)
    await user_command.create(
        account_id=account.id,
        nickname=request.nickname,
        gender=request.gender,
        birth_date=request.birth_date,
    )

    # トークン発行
    access_token = create_access_token(data={"sub": account.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """ログイン"""
    account_query = AccountQuery(db)
    account = await account_query.get_by_email(request.email)

    if not account or not verify_password(request.password, account.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )

    # リフレッシュトークン更新
    account_command = AccountCommand(db)
    refresh_token, expires_at = create_refresh_token()
    await account_command.update_refresh_token(
        account_id=account.id,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

    # トークン発行
    access_token = create_access_token(data={"sub": account.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> None:
    """ログアウト"""
    account_command = AccountCommand(db)
    await account_command.clear_refresh_token(current_account.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """トークンリフレッシュ"""
    account_query = AccountQuery(db)
    account = await account_query.get_by_refresh_token(request.refresh_token)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if not verify_refresh_token(account.refresh_token_expires_at):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # トークンローテーション
    account_command = AccountCommand(db)
    new_refresh_token, expires_at = create_refresh_token()
    await account_command.update_refresh_token(
        account_id=account.id,
        refresh_token=new_refresh_token,
        expires_at=expires_at,
    )

    access_token = create_access_token(data={"sub": account.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )
```

### 4.3 ユーザーエンドポイント

#### app/api/v1/endpoints/users.py

```python
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """現在のユーザー情報を取得"""
    return UserResponse.model_validate(current_user)
```

### 4.4 Pydanticスキーマ

#### app/schemas/auth.py

```python
from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.models.user import Gender


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    nickname: str = Field(..., min_length=1, max_length=100)
    gender: Gender
    birth_date: date


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

#### app/schemas/user.py

```python
from datetime import date, datetime

from pydantic import BaseModel

from app.models.user import Gender


class UserResponse(BaseModel):
    id: str
    nickname: str
    gender: Gender
    birth_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
```

### 4.5 認証依存関係

#### app/core/deps.py

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.query.account_query import AccountQuery
from app.query.user_query import UserQuery

security = HTTPBearer()


async def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Account:
    """現在のアカウントを取得"""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    account_id = payload.get("sub")
    if account_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    query = AccountQuery(db)
    account = await query.get_by_id(account_id)

    if account is None or not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or inactive",
        )

    return account


async def get_current_user(
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> User:
    """現在のユーザーを取得"""
    query = UserQuery(db)
    user = await query.get_by_account_id(current_account.id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
```

---

## 5. テストケース一覧

### 5.1 スキーマテスト（tests/schemas/test_auth_schema.py）

| テストケース | 説明 |
|-------------|------|
| test_signup_request_valid | 正常な入力でSignupRequestが作成される |
| test_signup_request_invalid_email | 不正なメール形式でValidationError |
| test_signup_request_short_password | 8文字未満のパスワードでValidationError |
| test_signup_request_empty_nickname | 空のニックネームでValidationError |
| test_signup_request_long_nickname | 100文字超のニックネームでValidationError |
| test_signup_request_invalid_gender | 不正なgender値でValidationError |
| test_login_request_valid | 正常な入力でLoginRequestが作成される |
| test_login_request_invalid_email | 不正なメール形式でValidationError |

### 5.2 認証APIテスト（tests/api/v1/endpoints/test_auth.py）

| テストケース | 説明 |
|-------------|------|
| test_signup_success | 正常なサインアップでトークンが返却される |
| test_login_success | 正常なログインでトークンが返却される |
| test_login_wrong_credentials | 認証情報が間違っている場合401エラー |
| test_logout_success | 正常なログアウトで204返却 |
| test_logout_invalidates_refresh_token | ログアウト後のリフレッシュトークンが無効化される |
| test_refresh_success | 正常なリフレッシュで新トークンが返却される |
| test_refresh_invalid_token | 無効なリフレッシュトークンで401エラー |
| test_refresh_expired_token | 期限切れリフレッシュトークンで401エラー |
| test_refresh_token_rotation | リフレッシュ後に古いトークンが無効化される |
| test_login_invalidates_other_sessions | 新規ログインで既存セッションが無効化される |

### 5.3 ユーザーAPIテスト（tests/api/v1/endpoints/test_users.py）

| テストケース | 説明 |
|-------------|------|
| test_get_me_success | 認証済みで自分のユーザー情報が取得できる |
