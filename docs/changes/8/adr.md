# ADR: Accountモデルの作成

## 1. 概要

パスワード認証・OAuth認証・パスキー（WebAuthn）認証の3方式に対応するため、認証アカウントモデル群を新設する。

既存の `users` テーブルは「ユーザープロフィール」としての役割を持つが、認証情報は `Account` モデルに分離する。1つのAccountは少なくとも1つの認証方式（Password / OAuth / PassKey）を持つ。

今回のスコープはモデル定義とマイグレーションの作成のみであり、APIエンドポイントは含まない。

## 2. ファイル構成

```
app/
├── models/
│   ├── __init__.py                 # モデルの re-export
│   ├── account.py                  # Account モデル
│   ├── account_password.py         # AccountPassword モデル
│   ├── account_oauth.py            # AccountOauth モデル
│   ├── account_passkey.py          # AccountPasskey モデル
│   └── refresh_token.py            # RefreshToken モデル
├── schemas/
│   └── account.py                  # Account 関連スキーマ
├── query/
│   └── account_query.py            # Account 読み取りクエリ
├── command/
│   └── account_command.py          # Account 書き込みコマンド
alembic/
└── versions/
    └── xxxx_create_account_tables.py  # マイグレーション
tests/
├── models/
│   ├── test_account.py
│   ├── test_account_password.py
│   ├── test_account_oauth.py
│   ├── test_account_passkey.py
│   └── test_refresh_token.py
└── query/
    └── test_account_query.py
```

## 3. モデリング案

### テーブル定義

#### accounts

| カラム | 型 | 制約 | 説明 |
|--------|------|------|------|
| id | Integer | PK, autoincrement | アカウントID |
| email | String(255) | UNIQUE, NOT NULL, INDEX | メールアドレス（ログイン識別子） |
| is_active | Boolean | NOT NULL, DEFAULT true | アカウント有効フラグ |
| created_at | DateTime(timezone) | NOT NULL, server_default=now() | 作成日時 |
| updated_at | DateTime(timezone) | NOT NULL, server_default=now() | 更新日時 |

#### account_passwords

| カラム | 型 | 制約 | 説明 |
|--------|------|------|------|
| id | Integer | PK, autoincrement | ID |
| account_id | Integer | FK(accounts.id), UNIQUE, NOT NULL | アカウントID（1:1） |
| hashed_password | String(255) | NOT NULL | bcryptハッシュ済みパスワード |
| created_at | DateTime(timezone) | NOT NULL, server_default=now() | 作成日時 |
| updated_at | DateTime(timezone) | NOT NULL, server_default=now() | 更新日時 |

#### account_oauths

| カラム | 型 | 制約 | 説明 |
|--------|------|------|------|
| id | Integer | PK, autoincrement | ID |
| account_id | Integer | FK(accounts.id), NOT NULL | アカウントID（1:N） |
| provider | String(50) | NOT NULL | OAuthプロバイダ名（google, github等） |
| provider_id | String(255) | NOT NULL | プロバイダ側のユーザーID |
| created_at | DateTime(timezone) | NOT NULL, server_default=now() | 作成日時 |
| updated_at | DateTime(timezone) | NOT NULL, server_default=now() | 更新日時 |

UNIQUE制約: (provider, provider_id)

#### account_passkeys

| カラム | 型 | 制約 | 説明 |
|--------|------|------|------|
| id | Integer | PK, autoincrement | ID |
| account_id | Integer | FK(accounts.id), NOT NULL | アカウントID（1:N） |
| credential_id | Text | UNIQUE, NOT NULL | パスキーの一意識別ID |
| public_key | Text | NOT NULL | 署名検証用の公開鍵 |
| sign_count | Integer | NOT NULL, DEFAULT 0 | クローン検知用の署名カウンタ |
| transports | String(255) | NULL | 接続方式（usb, nfc, ble, internal） |
| aaguid | String(36) | NULL | デバイスモデル識別ID |
| name | String(100) | NULL | ユーザーが設定するパスキーの表示名 |
| created_at | DateTime(timezone) | NOT NULL, server_default=now() | 作成日時 |
| updated_at | DateTime(timezone) | NOT NULL, server_default=now() | 更新日時 |

#### refresh_tokens

| カラム | 型 | 制約 | 説明 |
|--------|------|------|------|
| id | Integer | PK, autoincrement | ID |
| account_id | Integer | FK(accounts.id), NOT NULL | アカウントID |
| token | String(512) | UNIQUE, NOT NULL, INDEX | リフレッシュトークン |
| expires_at | DateTime(timezone) | NOT NULL | トークン有効期限 |
| revoked | Boolean | NOT NULL, DEFAULT false | 無効化フラグ |
| created_at | DateTime(timezone) | NOT NULL, server_default=now() | 作成日時 |

### ER図

```
accounts (1) ──── (0..1) account_passwords
accounts (1) ──── (0..N) account_oauths
accounts (1) ──── (0..N) account_passkeys
accounts (1) ──── (0..N) refresh_tokens
```

### モデルのライフサイクル

#### Account

1. **作成**: いずれかの認証方式で初回登録時に作成される
2. **有効**: `is_active=True` の状態で各認証方式でログイン可能
3. **無効化**: `is_active=False` に更新することでログインを停止
4. **削除**: CASCADE により関連する認証情報もすべて削除

#### AccountPassword

1. **作成**: パスワード認証での新規登録時に作成
2. **更新**: パスワード変更時に `hashed_password` を更新
3. **削除**: パスワード認証を無効化する際に削除（他の認証方式が存在する場合のみ）

#### AccountOauth

1. **作成**: OAuthプロバイダでの初回認証時に作成
2. **削除**: OAuth連携解除時に削除（他の認証方式が存在する場合のみ）

#### RefreshToken

1. **作成**: ログイン成功時に発行
2. **無効化**: ログアウト時またはトークンリフレッシュ時に `revoked=True` に更新
3. **期限切れ**: `expires_at` を過ぎたトークンは無効として扱う

#### AccountPasskey

1. **作成**: パスキー登録フロー完了時に作成
2. **更新**: 認証ごとに `sign_count` をインクリメント
3. **削除**: パスキー削除時に削除（他の認証方式が存在する場合のみ）

### ビジネスルール

- Account は少なくとも1つの認証方式（Password / OAuth / PassKey）を持たなければならない
- 認証方式の削除時、他に認証方式が存在しない場合は削除を拒否する
- email は全アカウントで一意でなければならない
- OAuthの (provider, provider_id) の組み合わせは一意でなければならない
- PassKeyの credential_id は一意でなければならない
- sign_count は認証ごとに単調増加しなければならない（クローン検知）

## 4. スキーマ設計

### Request

```python
class AccountCreateRequest(BaseModel):
    """アカウント作成リクエスト（パスワード認証）"""
    email: EmailStr
    password: str  # min_length=8

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
```

### Response

```python
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
```

## 5. テストケース一覧

### モデルテスト

#### test_account.py
- Account を作成できること
- email が一意制約に違反した場合エラーになること
- is_active のデフォルト値が True であること
- created_at, updated_at が自動設定されること

#### test_account_password.py
- AccountPassword を Account に紐づけて作成できること
- 同一 Account に対して複数の AccountPassword を作成するとエラーになること（UNIQUE制約）

#### test_account_oauth.py
- AccountOauth を Account に紐づけて作成できること
- 同一 Account に対して複数の provider で AccountOauth を作成できること
- (provider, provider_id) の重複でエラーになること

#### test_account_passkey.py
- AccountPasskey を Account に紐づけて作成できること
- 同一 Account に対して複数のパスキーを登録できること
- credential_id の重複でエラーになること
- sign_count のデフォルト値が 0 であること

### クエリテスト

#### test_account_query.py
- account_id で Account を取得できること（get）
- email で Account を取得できること（get）
- 存在しない Account を取得すると None が返ること
- Account に紐づく認証方式を含めて取得できること

#### test_refresh_token.py
- RefreshToken を Account に紐づけて作成できること
- token が一意制約に違反した場合エラーになること
- revoked のデフォルト値が False であること
