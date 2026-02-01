# Web Template - システムアーキテクチャ

## 概要

Web開発する時のテンプレート

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| 言語 | Python 3.x |
| Webフレームワーク | FastAPI |
| データベース | PostgreSQL 16 |
| ORM | SQLAlchemy (非同期) |
| マイグレーション | Alembic |
| 認証 | JWT (python-jose) + bcrypt (passlib) |
| LLM | OpenAI API (gpt-4o-mini) |
| コンテナ | Docker + Docker Compose |
| ASGIサーバー | Uvicorn |

## ディレクトリ構造

```
system_name/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーションのエントリーポイント
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/              # API v1 エンドポイント
│   │       ├── __init__.py
│   │       ├── api.py       # v1 ルーター集約
│   │       ├── endpoints/   # 公開APIエンドポイント
│   │       │   └── ...
│   │       ├── admin/       # 管理者向けAPIエンドポイント
│   │       │   └── ...
│   │       └── internal/    # 内部向けAPIエンドポイント
│   │           └── ...
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # アプリケーション設定（pydantic-settings）
│   │   └── security.py      # JWT認証、パスワードハッシュ
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # SQLAlchemy Base
│   │   └── session.py       # 非同期DBセッション管理
│   ├── models/              # SQLAlchemyモデル
│   │   └── __init__.py
│   ├── schemas/             # Pydanticスキーマ（リクエスト/レスポンス）
│   │   └── __init__.py
│   ├── query/               # 読み取り専用クエリ（CQRS - Query側）
│   │   └── ...
│   ├── command/             # 書き込み操作コマンド（CQRS - Command側）
│   │   └── ...
│   └── usecase/             # ビジネスロジック・ユースケース
│       └── ...
├── alembic/
│   ├── env.py               # Alembic設定
│   └── versions/            # マイグレーションファイル
├── tests/                   # テストディレクトリ
├── docker-compose.yml       # Docker Compose設定
├── Dockerfile               # Dockerイメージ定義
└── .env                     # 環境変数（gitignore対象）
```

## Docker構成

### サービス

1. **app**: FastAPIアプリケーション
   - ポート: 8000
   - 開発時はホットリロード有効

2. **db**: PostgreSQL 16
   - ポート: 5432
   - ヘルスチェック付き
   - データ永続化（named volume）
