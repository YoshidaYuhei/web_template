---
name: "ADR"
description: requirement.md を参照して 設計書である adr.md を作成する
---
usage:
  どのIssueに対する指示かわからない場合、Issue番号を要求する

## 出力
  path: docs/changes/<issue_id>/requirement.md
  format: markdown
  items: 
    why: なぜその機能が必要なのかを説明する
    ux: 提供したいユーザー体験を記述する
    issue: 解決したい課題を記述する
    usecase: 想定されるユースケースをリストアップする
    specdelta: 既存の仕様との差分を説明する

step:
  1. docs/changes/<issue_id>/requirement.md を読み込む
  2. 既存のコードを読み込み、どこを修正・追加するのか把握する
  3. モデリングが必要な場合、.claude/guidelines/modeling.md を読み込んで、モデリングの設計を行う
  4. APIが必要な場合、スキーマの設計をする
  5. Controllerを記述する
  6. 必要なテストケースをリスト化する

**出力構成**
adr.md の構成
1. 概要
2. ファイル構成(architect.mdのディレクトリ構造に準拠すること)
3. モデリング案
  - テーブル定義
  - モデルのライフサイクル
  - ビジネスルール
3. スキーマ設計
  - Request と Response を分離する
  - 既存のスキーマが使える場合、そのまま再利用またはラップする
4. API設計(api/v1/api.py に対する記述は不要)
5. テストケース一覧(テストコード例は不要)
