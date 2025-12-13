# Health API Spec Delta

## ADDED Requirements

### Requirement: ヘルスチェックスキーマの定義

アプリケーションは、ヘルスチェックレスポンスを表現する Pydantic スキーマを提供 MUST。

#### Scenario: 正常時のレスポンス構造
- Given: アプリケーションが正常に動作している
- When: `/health` エンドポイントにGETリクエストを送信する
- Then: 以下のフィールドを含むJSONレスポンスが返される
  - `status`: "healthy" または "unhealthy"
  - `database`: データベース接続状態オブジェクト

### Requirement: データベース接続確認

ヘルスチェックAPIは、MySQLデータベースへの接続状態を確認 MUST。

#### Scenario: データベース接続成功
- Given: MySQLデータベースが正常に稼働している
- When: `/health` エンドポイントにGETリクエストを送信する
- Then: HTTP 200 ステータスコードが返される
- And: `database.status` が "connected" である

#### Scenario: データベース接続失敗
- Given: MySQLデータベースに接続できない
- When: `/health` エンドポイントにGETリクエストを送信する
- Then: HTTP 503 ステータスコードが返される
- And: `status` が "unhealthy" である
- And: `database.status` が "disconnected" である
- And: `database.error` にエラーメッセージが含まれる

## MODIFIED Requirements

### Requirement: ヘルスチェックエンドポイントの更新

既存の `/health` エンドポイントは、構造化されたレスポンススキーマを使用するように更新 MUST。

#### Scenario: OpenAPIスキーマへの反映
- Given: FastAPIアプリケーションが起動している
- When: `/docs` または `/openapi.json` にアクセスする
- Then: `/health` エンドポイントのレスポンススキーマが正しく表示される
