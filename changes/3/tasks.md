# タスクリスト: ログイン機能を追加する

**Issue:** #3
**ADR:** [adr.md](./adr.md)

---

## モデル

### Accountモデル
- [ ] Accountモデルのテストコードを追加する (`tests/models/test_account.py`)
- [ ] Accountモデルを追加する (`app/models/account.py`)

### Userモデル
- [ ] Userモデルのテストコードを追加する (`tests/models/test_user.py`)
- [ ] Userモデルを追加する (`app/models/user.py`)

### モデルエクスポート
- [ ] `app/models/__init__.py` にAccount, Userをエクスポートする

---

## マイグレーション

- [ ] Alembicマイグレーションファイルを作成する (`alembic/versions/xxxx_create_account_and_user_tables.py`)

---

## 設定・セキュリティ

### Config修正
- [ ] `app/core/config.py` に `refresh_token_expire_days` を追加する

### Security修正
- [ ] `app/core/security.py` に `create_refresh_token` を追加する
- [ ] `app/core/security.py` に `verify_refresh_token` を追加する

### 認証依存関係
- [ ] `app/core/deps.py` を新規作成する（`get_current_account`, `get_current_user`）

---

## スキーマ

### 認証スキーマ
- [ ] 認証スキーマのテストコードを追加する (`tests/schemas/test_auth_schema.py`)
- [ ] 認証スキーマを追加する (`app/schemas/auth.py`)

### ユーザースキーマ
- [ ] ユーザースキーマを追加する (`app/schemas/user.py`)

### スキーマエクスポート
- [ ] `app/schemas/__init__.py` に認証・ユーザースキーマをエクスポートする

---

## Query

### AccountQuery
- [ ] AccountQueryのテストコードを追加する (`tests/query/test_account_query.py`)
- [ ] AccountQueryを追加する (`app/query/account_query.py`)

### UserQuery
- [ ] UserQueryのテストコードを追加する (`tests/query/test_user_query.py`)
- [ ] UserQueryを追加する (`app/query/user_query.py`)

---

## Command

### AccountCommand
- [ ] AccountCommandのテストコードを追加する (`tests/command/test_account_command.py`)
- [ ] AccountCommandを追加する (`app/command/account_command.py`)

### UserCommand
- [ ] UserCommandのテストコードを追加する (`tests/command/test_user_command.py`)
- [ ] UserCommandを追加する (`app/command/user_command.py`)

---

## テストフィクスチャ

- [ ] `tests/conftest.py` にAccount/Userテスト用フィクスチャを追加する

---

## ルーティング

- [ ] `app/api/v1/api.py` に auth, users ルーターを追加する

---

## サインアップAPI (POST /api/v1/auth/signup)

- [ ] サインアップAPIのテストコードを追加する (`tests/api/v1/endpoints/test_auth.py::test_signup_*`)
- [ ] サインアップAPIを実装する (`app/api/v1/endpoints/auth.py::signup`)

---

## ログインAPI (POST /api/v1/auth/login)

- [ ] ログインAPIのテストコードを追加する (`tests/api/v1/endpoints/test_auth.py::test_login_*`)
- [ ] ログインAPIを実装する (`app/api/v1/endpoints/auth.py::login`)

---

## ログアウトAPI (POST /api/v1/auth/logout)

- [ ] ログアウトAPIのテストコードを追加する (`tests/api/v1/endpoints/test_auth.py::test_logout_*`)
- [ ] ログアウトAPIを実装する (`app/api/v1/endpoints/auth.py::logout`)

---

## トークンリフレッシュAPI (POST /api/v1/auth/refresh)

- [ ] トークンリフレッシュAPIのテストコードを追加する (`tests/api/v1/endpoints/test_auth.py::test_refresh_*`)
- [ ] トークンリフレッシュAPIを実装する (`app/api/v1/endpoints/auth.py::refresh`)

---

## ユーザー情報取得API (GET /api/v1/users/me)

- [ ] ユーザー情報取得APIのテストコードを追加する (`tests/api/v1/endpoints/test_users.py::test_get_me_*`)
- [ ] ユーザー情報取得APIを実装する (`app/api/v1/endpoints/users.py::get_me`)
