---
name: "OpenSpec: ADR"
description: proposal.md を参照して design.md を作成する
category: OpenSpec
tags: [openspec, change]
---
<!-- OPENSPEC:START -->
**ガードレール**
- 引数として change_id を取る。change_id ディレクトリ内になる proposal.md を読んで設計を行う
- 新しいモデルが必要ならスキーマの構成を書く
- 新しいAPIが必要ならFastAPIの Controller の実装例を書く


**手順**
1. `openspec/project.md`を確認し、`openspec list`と`openspec list --specs`を実行し、関連するコードやドキュメント（例：`rg`/`ls`経由）を調査して、提案を現在の動作に基づかせる；明確化が必要なギャップをメモする。
2. 一意の動詞で始まる`change-id`を選択し、`openspec/changes/<id>/`の下に`proposal.md`を作成する
3. 変更を具体的な機能または要件にマッピングし、複数スコープの作業を明確な関係と順序を持つ個別のスペックデルタに分割する。
4. `changes/<id>/specs/<capability>/spec.md`（機能ごとに1つのフォルダ）にスペックデルタを作成し、`## ADDED|MODIFIED|REMOVED Requirements`を使用して要件ごとに少なくとも1つの`#### Scenario:`を含め、関連する場合は関連機能を相互参照する。
5. `openspec validate <id> --strict`で検証し、提案を共有する前にすべての問題を解決する。

**出力構成**
design.md の構成
1. 概要
2. ファイル構成(architect.mdのディレクトリ構造に準拠すること)
3. スキーマ設計
4. API設計(api/v1/api.py に対する記述は不要)
5. テストケース一覧(テストコード例は不要)
<!-- OPENSPEC:END -->
