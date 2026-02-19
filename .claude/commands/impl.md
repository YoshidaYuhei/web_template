---
name: "Implement"
description: adr.md を参照してコーディングを行う
---
usage:
  どのIssueに対する指示かわからない場合、Issue番号を要求する
  adr.md の設計に基づいて、tasks.md の順番に従ってコーディングを行う
  ユーザーの承認は求めずにテストまで実行し、テストが通ればPullRequestを作成して push してください
  テストで通らなかった場合、何が通らなかったかを tasks.md に記述し、作業を停止してください

step:
  1. `.claude/gudelines/testcode.md`と`.claude/gudelines/design_pattern.md`を読み込む
  2. `.changes/<issue_id>/adr.md`と`.changes/<issue_id>/tasks.md`を読み込む
  3. adr.md の設計に基づいて、tasks.md の順番に従ってコーディングを行う
  4. 各タスクについて実装が完了し、テストがPassしたら tasks.md のチェックボックスにチェックをいれて次に進む
