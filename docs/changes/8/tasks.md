# Issue #8 タスク一覧: Accountモデルの作成

## モデル

### Account
- [x] `tests/models/test_account.py` にテストコードを追加する
- [x] `app/models/account.py` に Account モデルを追加する

### AccountPassword
- [x] `tests/models/test_account_password.py` にテストコードを追加する
- [x] `app/models/account_password.py` に AccountPassword モデルを追加する

### AccountOauth
- [x] `tests/models/test_account_oauth.py` にテストコードを追加する
- [x] `app/models/account_oauth.py` に AccountOauth モデルを追加する

### AccountPasskey
- [x] `tests/models/test_account_passkey.py` にテストコードを追加する
- [x] `app/models/account_passkey.py` に AccountPasskey モデルを追加する

### RefreshToken
- [x] `tests/models/test_refresh_token.py` にテストコードを追加する
- [x] `app/models/refresh_token.py` に RefreshToken モデルを追加する

### re-export
- [x] `app/models/__init__.py` に全モデルの re-export を追加する

## マイグレーション
- [ ] Alembic マイグレーションファイルを生成する（accounts, account_passwords, account_oauths, account_passkeys, refresh_tokens）

## テストフィクスチャ
- [x] `tests/conftest.py` に Account 関連のファクトリフィクスチャを追加する

## クエリ
- [x] `tests/query/test_account_query.py` にテストコードを追加する
- [x] `app/query/account_query.py` に Account 読み取りクエリを実装する

## コマンド
- [x] `app/command/account_command.py` に Account 書き込みコマンドを実装する

## スキーマ
- [x] `app/schemas/account.py` に Request / Response スキーマを追加する
