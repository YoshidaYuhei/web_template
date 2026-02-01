# web_template

## 技術スタック
### backend
言語: Python
フレームワーク: FastAPI
DB: Postgresql

### frontend
言語: Typescript
フレームワーク: React
ビルドツール: Vite

### infra
言語: teraform
プラットフォーム: AWS

## 仕様駆動開発の運用
docs ディレクトリに仕様を全て書く。
docs/changes は 実装時の差分を保存するディレクトリで、Issue番号をディレクトリ名とする
  - changes 配下には 要求スコープ(requirements.md), 設計(adr.md), タスク一覧(tasks.md) が保存される
  - 本番リリースされた差分は ssot(Single Source of Truth)ディレクトリ配下のドキュメントに統合される。(applyコマンド)

## セットアップ

```bash
# 依存パッケージのインストール
uv sync --all-extras
```

## テストの実行

```bash
# 全テストを実行
uv run pytest

# 詳細出力で実行
uv run pytest -v

# 特定のディレクトリのテストを実行
uv run pytest tests/models/
uv run pytest tests/api/

# カバレッジ付きで実行
uv run pytest --cov=app
```

## OpenTofu


## 注意点
  - ローカル環境でホスト側は一般的なポート番号は利用しないように（他のシステムと競合します）
    - ex. 8001:8000

