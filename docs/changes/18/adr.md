# ADR: パスワード認証によるサインアップAPIの作成

## 1. 概要

ユーザーがメールアドレスとパスワードでアカウントを新規作成するためのサインアップAPIエンドポイントを作成する。

既存のモデル層（Account, AccountPassword, RefreshToken）、セキュリティユーティリティ（JWT生成・パスワードハッシュ化）、CQRS層（AccountCommand, AccountQuery）はすべて実装済みであり、これらを組み合わせてサインアップのユースケースとAPIエンドポイントを構築する。

サインアップ成功時は即座にログイン状態となり、アクセストークンとリフレッシュトークンを返却する。

## 2. ファイル構成

```
app/
├── api/
│   └── v1/
│       ├── api.py                          # 認証ルーターの登録を追加（既存変更）
│       └── endpoints/
│           └── auth.py                     # 認証エンドポイント（新規作成）
├── schemas/
│   ├── account.py                          # パスワードバリデーション追加（既存変更）
│   └── auth.py                             # 認証レスポンススキーマ（新規作成）
└── usecase/
    └── signup_usecase.py                   # サインアップユースケース（新規作成）
tests/
├── api/
│   └── v1/
│       └── endpoints/
│           └── test_auth_signup.py          # サインアップAPIテスト（新規作成）
└── usecase/
    └── test_signup_usecase.py              # サインアップユースケーステスト（新規作成）
```

## 3. モデリング案

### テーブル定義

新規テーブルの追加はなし。既存テーブルをそのまま利用する。

| テーブル | 用途 |
|---------|------|
| accounts | アカウント本体の作成 |
| account_passwords | ハッシュ化パスワードの保存 |
| refresh_tokens | リフレッシュトークンの保存 |

### モデルのライフサイクル

サインアップ時の処理フロー:

1. **Account 作成**: `AccountCommand.create_account(email)` でアカウントを作成
2. **AccountPassword 作成**: `AccountCommand.create_password(account_id, hashed_password)` でパスワードを保存
3. **RefreshToken 作成**: `AccountCommand.create_refresh_token(account_id, token, expires_at)` でリフレッシュトークンを発行
4. **AccessToken 生成**: `create_access_token({"sub": str(account_id)})` でアクセストークンを生成（DB保存なし）

上記 1〜3 は単一トランザクション内で実行し、いずれかが失敗した場合はすべてロールバックする。

### ビジネスルール

- メールアドレスは全アカウントで一意でなければならない（重複時は 409 Conflict）
- パスワードは最低8文字以上でなければならない
- パスワードは bcrypt でハッシュ化して保存する（平文保存禁止）
- サインアップ成功時はアクセストークンとリフレッシュトークンを即時発行する
- リフレッシュトークンは `secrets.token_urlsafe()` で生成する
- リフレッシュトークンの有効期限は7日間とする

## 4. スキーマ設計

### Request

既存の `AccountCreateRequest` を利用する。パスワードのバリデーションを追加する。

```python
# app/schemas/account.py（既存変更）
class AccountCreateRequest(BaseModel):
    """アカウント作成リクエスト（パスワード認証）"""
    email: EmailStr
    password: str = Field(..., min_length=8)
```

### Response

認証レスポンス用のスキーマを新規作成する。

```python
# app/schemas/auth.py（新規作成）
class TokenResponse(BaseModel):
    """トークンレスポンス"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class SignupResponse(BaseModel):
    """サインアップレスポンス"""
    account: AccountResponse
    token: TokenResponse
```

## 5. API設計

### POST /api/v1/auth/signup/password

パスワード認証によるサインアップ。

```python
# app/api/v1/endpoints/auth.py
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup/password", response_model=SignupResponse, status_code=201)
async def signup_with_password(
    request: AccountCreateRequest,
    session: AsyncSession = Depends(get_db),
) -> SignupResponse:
```

| 項目 | 値 |
|------|-----|
| メソッド | POST |
| パス | `/api/v1/auth/signup/password` |
| リクエスト | `AccountCreateRequest` (email, password) |
| レスポンス | `SignupResponse` (account + token) |
| 成功ステータス | 201 Created |
| エラー | 409 Conflict（メール重複）, 422 Unprocessable Entity（バリデーションエラー） |

## 6. テストケース一覧

### ユースケーステスト（test_signup_usecase.py）

- 正常にサインアップできること（Account, AccountPassword, RefreshToken が作成される）
- アクセストークンとリフレッシュトークンが返却されること
- パスワードが bcrypt でハッシュ化されて保存されること
- 重複メールアドレスの場合に例外が発生すること

### APIテスト（test_auth_signup.py）

- POST /api/v1/auth/signup/password で正常にサインアップできること（201）
- レスポンスにアカウント情報（id, email, is_active）が含まれること
- レスポンスにトークン情報（access_token, refresh_token, token_type）が含まれること
- 重複メールアドレスの場合 409 が返却されること
