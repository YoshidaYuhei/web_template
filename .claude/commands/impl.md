---
name: "Implement"
description: adr.md を参照してコーディングを行う
---
usage:
  どのIssueに対する指示かわからない場合、Issue番号を要求する
  adr.md の設計に基づいて、tasks.md の順番に従ってコーディングを行う
  各ステップでユーザーからの承認を求めること

step:
  1. `.claude/gudelines/testcode.md`と`.claude/gudelines/design_pattern.md`を読み込む
  2. `.changes/<issue_id>/adr.md`と`.changes/<issue_id>/tasks.md`を読み込む
  3. adr.md の設計に基づいて、tasks.md の順番に従ってコーディングを行う
  4. 各タスクについて実装が完了し、テストがPassしたら tasks.md のチェックボックスにチェックをいれて次に進む
