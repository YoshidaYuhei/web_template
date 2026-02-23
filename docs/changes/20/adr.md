# ADR: パスワード認証によるサインアップ画面の作成

## 1. 概要

バックエンドのサインアップAPI（`POST /auth/signup/password`）に接続するフロントエンドのサインアップ画面を作成する。

React Router によるクライアントサイドルーティングを導入し、Tailwind CSS でUIを構築する。フロントエンド側でバリデーションを行い、APIエラーも適切に画面表示する。サインアップ成功後はダッシュボード画面（プレースホルダー）に遷移する。トークンの永続化は本issueのスコープ外とする。

## 2. ファイル構成

```
frontend/
├── src/
│   ├── main.tsx                          # BrowserRouterの設定（既存変更）
│   ├── App.tsx                           # ルート定義（既存変更）
│   ├── index.css                         # Tailwind CSS読み込み（既存変更）
│   ├── pages/
│   │   ├── SignupPage.tsx                # サインアップ画面（新規作成）
│   │   └── DashboardPage.tsx             # ダッシュボード画面・プレースホルダー（新規作成）
│   └── lib/
│       └── api.ts                        # API呼び出しユーティリティ（新規作成）
├── package.json                          # 依存関係追加（既存変更）
└── vite.config.ts                        # Tailwindプラグイン追加（既存変更）
```

## 3. モデリング案

### テーブル定義

フロントエンドのみの変更のため、テーブルの追加・変更はなし。

### モデルのライフサイクル

フロントエンドからのデータフロー:

1. ユーザーがフォームにメールアドレス・パスワードを入力
2. フロントエンドバリデーション（メール形式、パスワード8文字以上）
3. バリデーション通過後、`POST /api/auth/signup/password` にリクエスト送信
4. 成功(201): レスポンス受信 → ダッシュボード画面へ遷移
5. 失敗(409/422/ネットワークエラー): エラーメッセージを画面に表示

### ビジネスルール

- メールアドレスは有効なメール形式であること（フロントエンド検証）
- パスワードは8文字以上であること（フロントエンド検証、バックエンドでも検証済み）
- フロントエンドバリデーション不通過時はAPIリクエストを送信しない
- APIエラー時はステータスコードに応じたメッセージを表示する
  - 409: 「このメールアドレスは既に登録されています」
  - 422: バックエンドのバリデーションエラーメッセージを表示
  - ネットワークエラー: 「サーバーに接続できません。しばらくしてから再試行してください」
- トークンは今回保存しない（後続issueで対応）

## 4. スキーマ設計

### Request（フロントエンド → バックエンド）

バックエンドの `AccountCreateRequest` に合わせた型定義。

```typescript
// フォーム入力の型
interface SignupForm {
  email: string
  password: string
}

// APIリクエストボディ（SignupFormと同一構造）
interface SignupRequest {
  email: string
  password: string
}
```

### Response（バックエンド → フロントエンド）

バックエンドの `SignupResponse` に対応する型定義。

```typescript
interface AccountResponse {
  id: number
  email: string
  is_active: boolean
  has_password: boolean
  oauth_providers: string[]
  passkey_count: number
  created_at: string
}

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

interface SignupResponse {
  account: AccountResponse
  token: TokenResponse
}
```

### エラーレスポンス

FastAPIのHTTPExceptionに準拠。

```typescript
// 409 Conflict
interface ErrorResponse {
  detail: string
}

// 422 Validation Error
interface ValidationErrorResponse {
  detail: Array<{
    loc: (string | number)[]
    msg: string
    type: string
  }>
}
```

## 5. API設計

フロントエンドからのAPI呼び出し設計。バックエンドの変更はなし。

### POST /api/auth/signup/password

Viteプロキシ経由でバックエンドの `POST /auth/signup/password` に転送される。

| 項目 | 値 |
|------|-----|
| メソッド | POST |
| フロントエンドURL | `/api/auth/signup/password` |
| バックエンドURL | `/auth/signup/password`（プロキシが `/api` を除去） |
| Content-Type | `application/json` |
| リクエストボディ | `{ email: string, password: string }` |
| 成功レスポンス | 201: `SignupResponse` |
| エラーレスポンス | 409: `ErrorResponse`, 422: `ValidationErrorResponse` |

### APIクライアント設計（`lib/api.ts`）

```typescript
async function signup(request: SignupRequest): Promise<SignupResponse>
```

- `fetch` APIを使用（外部HTTPライブラリは追加しない）
- 成功時: `SignupResponse` を返す
- エラー時: ステータスコードに応じた例外をスローする

## 6. テストケース一覧

### SignupPage コンポーネントテスト

- メールアドレスとパスワードの入力欄、サインアップボタンが表示されること
- メールアドレスが空の状態で送信するとバリデーションエラーが表示されること
- メールアドレスの形式が不正な場合にバリデーションエラーが表示されること
- パスワードが空の状態で送信するとバリデーションエラーが表示されること
- パスワードが8文字未満の場合にバリデーションエラーが表示されること
- バリデーションエラー時にAPIリクエストが送信されないこと
- 正常な入力でサインアップボタンを押すとAPIリクエストが送信されること
- API成功時(201)にダッシュボード画面（`/`）に遷移すること
- API失敗時(409)に重複メールのエラーメッセージが表示されること
- API失敗時(422)にバリデーションエラーメッセージが表示されること
- ネットワークエラー時にサーバー接続エラーメッセージが表示されること
- API呼び出し中はサインアップボタンがローディング状態になること

### APIクライアントテスト（`lib/api.ts`）

- 正常なリクエストでSignupResponseが返却されること
- 409エラー時にエラー情報が取得できること
- 422エラー時にバリデーションエラー情報が取得できること
- ネットワークエラー時に適切な例外がスローされること

### DashboardPage コンポーネントテスト

- プレースホルダーのダッシュボード画面が表示されること
