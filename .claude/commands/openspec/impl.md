---
name: "OpenSpec: Impliment"
description: design.md, tasks.md を参照して実装する
category: OpenSpec
tags: [openspec, change]
---
<!-- OPENSPEC:START -->
**ガードレール**
- 引数として change_id を取る。change_id ディレクトリ内になる design.md, tasks.md を読んで実装を行う
- 実装する前に openspec/guideline内にあるファイルを全て参照する
- テストコードを実装する時はできるだけスタブしないように

**手順**
1. 引数として change_id を取る。change_id ディレクトリ内になる design.md, tasks.md を読んで何をすべきか把握する
2. テストするユースケースを整理して一覧で表示し、表示内容で相違ないか人間側に確認する
3. 承認されればテストコードを実装する
4. tasks.md の順序に従って実装する
5. テストコードを実行して追加・更新したテストコードが全てPassすることを確認する

**参考**
<!-- OPENSPEC:END -->
