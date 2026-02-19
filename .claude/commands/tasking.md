---
name: tasking
description: adr.md から実装計画を立て、タスクに分割してリスト化する
---

usage:
  どのIssueに対する指示かわからない場合、Issue番号を要求する
  adr.md からやることをリスト化する
  実装が完了したらテストを実行し、全て通ればPullRequestを作成して push してください

output:
  path: changes/<issue_id>/tasks.md
  format: markdown

rule:
  モデリングとAPIで分離する
  APIごとに区切る(commitの単位を分けたいから)
  追加、修正対象となるクラスごとにリスト化する。
  実装には依存関係があるため順番には注意すること
  - 例
  ```
  ## モデル
    - xxxモデルのテストコードを追加する
    - xxxモデルを追加する
  ## テストフィクスチャ
  ## ルーティング
  ## 更新API
    - 更新Requestと更新Responseのschemaを追加する
    - UseCaseのテストコードを追加する
    - Commandのテストコードを追加する
    - APIのテストコードを追加する
    - UseCase を実装する
    - Command を実装する
    - API を実装する
  
  実装が完了したらテストを実行し、全て通ればPullRequestを作成して push してください。
  テストが通らない場合、tasks.md に通らなかったテストを報告して作業を停止してください。
