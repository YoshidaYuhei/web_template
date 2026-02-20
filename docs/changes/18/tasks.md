# タスク一覧: パスワード認証によるサインアップAPI (#18)

## スキーマ

- [x] `app/schemas/account.py` の `AccountCreateRequest.password` に `min_length=8` バリデーションを追加する
- [x] `app/schemas/auth.py` を新規作成し、`TokenResponse` と `SignupResponse` を追加する

## ルーティング

- [x] `app/api/v1/endpoints/__init__.py` を作成する
- [x] `app/api/v1/api.py` に認証ルーターの登録を追加する

## サインアップAPI

- [x] `SignupUseCase` のテストコードを追加する（`tests/usecase/test_signup_usecase.py`）
- [x] APIのテストコードを追加する（`tests/api/v1/endpoints/test_auth_signup.py`）
- [x] `SignupUseCase` を実装する（`app/usecase/signup_usecase.py`）
- [x] APIエンドポイントを実装する（`app/api/v1/endpoints/auth.py`）

## 最終確認

- [x] テストを実行し、全て通ることを確認する（32 passed）
- [x] Pull Request を作成して push する → https://github.com/YoshidaYuhei/web_template/pull/19
