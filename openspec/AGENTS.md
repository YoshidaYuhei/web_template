# OpenSpec 指示書

AIコーディングアシスタント向けの、OpenSpecを使用したスペック駆動開発の指示書です。

## TL;DR クイックチェックリスト

- 既存の作業を検索: `openspec spec list --long`、`openspec list`（全文検索には`rg`のみ使用）
- スコープを決定: 新機能 vs 既存機能の変更
- 一意の`change-id`を選択: ケバブケース、動詞で始める（`add-`、`update-`、`remove-`、`refactor-`）
- デルタを記述: `## ADDED|MODIFIED|REMOVED|RENAMED Requirements`を使用；要件ごとに少なくとも1つの`#### Scenario:`を含める
- 検証: `openspec validate [change-id] --strict`で問題を修正
- 承認を要求: 提案が承認されるまで実装を開始しない

## 3段階ワークフロー

### 段階1: 変更の作成
以下の場合に提案を作成:
- 機能追加
- 破壊的変更（API、スキーマ）
- アーキテクチャやパターンの変更
- パフォーマンス最適化（動作が変わる場合）
- セキュリティパターンの更新

トリガー（例）:
- 「変更提案の作成を手伝って」
- 「変更を計画するのを手伝って」
- 「提案を作成したい」
- 「スペック提案を作成したい」
- 「スペックを作成したい」

緩やかなマッチングガイダンス:
- 以下のいずれかを含む: `proposal`、`change`、`spec`
- 以下のいずれかと組み合わせ: `create`、`plan`、`make`、`start`、`help`

提案をスキップする場合:
- バグ修正（意図した動作の復元）
- タイポ、フォーマット、コメント
- 依存関係の更新（非破壊的）
- 設定変更
- 既存動作のテスト

**ワークフロー**
1. `openspec/project.md`、`openspec list`、`openspec list --specs`を確認して現在のコンテキストを理解する。
2. 一意の動詞で始まる`change-id`を選択し、`openspec/changes/<id>/`の下に`proposal.md`を作成する。
3. `openspec/changes/<id>/`の下に`proposal.md`が作成されれば `openspec:adr` コマンドでArchitectureDesitionRecord(`adr.md`ファイル)を作成する。
4. `adr.md` を下に具体的に何をしなければいけないかをリスト化し、`tasks.md` を作成する
5. `## ADDED|MODIFIED|REMOVED Requirements`を使用してスペックデルタを作成し、要件ごとに少なくとも1つの`#### Scenario:`を含める。
6. `openspec validate <id> --strict`を実行し、提案を共有する前に問題を解決する。

### 段階2: 変更の実装
これらのステップをTODOとして追跡し、1つずつ完了する。
1. **proposal.mdを読む** - 何を構築するか理解する
2. **design.mdを読む**（存在する場合）- 技術的決定を確認する
3. **tasks.mdを読む** - 実装チェックリストを取得する
4. **タスクを順番に実装** - 順番に完了する
5. **完了を確認** - ステータスを更新する前に`tasks.md`のすべての項目が完了していることを確認する
6. **チェックリストを更新** - すべての作業が完了したら、リストが現実を反映するようにすべてのタスクを`- [x]`に設定する
7. **承認ゲート** - 提案がレビューおよび承認されるまで実装を開始しない

### 段階3: 変更のアーカイブ
デプロイ後、別のPRを作成して:
- `changes/[name]/` → `changes/archive/YYYY-MM-DD-[name]/`に移動
- 機能が変更された場合は`specs/`を更新
- ツーリングのみの変更には`openspec archive <change-id> --skip-specs --yes`を使用（常にchange IDを明示的に渡す）
- `openspec validate --strict`を実行して、アーカイブされた変更がチェックに合格することを確認

## タスク開始前

**コンテキストチェックリスト:**
- [ ] `specs/[capability]/spec.md`の関連スペックを読む
- [ ] `changes/`の保留中の変更を確認して競合がないか確認
- [ ] `openspec/project.md`を読んで規約を確認
- [ ] `openspec list`を実行してアクティブな変更を確認
- [ ] `openspec list --specs`を実行して既存の機能を確認

**スペック作成前:**
- 機能が既に存在するか常に確認する
- 重複を作成するより既存スペックの変更を優先する
- `openspec show [spec]`を使用して現在の状態を確認する
- リクエストが曖昧な場合、スキャフォールド前に1〜2の明確化質問をする

### 検索ガイダンス
- スペックの列挙: `openspec spec list --long`（スクリプト用には`--json`）
- 変更の列挙: `openspec list`（`openspec change list --json`も利用可能だが非推奨）
- 詳細表示:
  - スペック: `openspec show <spec-id> --type spec`（フィルター用に`--json`を使用）
  - 変更: `openspec show <change-id> --json --deltas-only`
- 全文検索（ripgrepを使用）: `rg -n "Requirement:|Scenario:" openspec/specs`

## クイックスタート

### CLIコマンド

```bash
# 基本コマンド
openspec list                  # アクティブな変更を一覧表示
openspec list --specs          # 仕様を一覧表示
openspec show [item]           # 変更またはスペックを表示
openspec validate [item]       # 変更またはスペックを検証
openspec archive <change-id> [--yes|-y]   # デプロイ後にアーカイブ（非対話モードには--yesを追加）

# プロジェクト管理
openspec init [path]           # OpenSpecを初期化
openspec update [path]         # 指示ファイルを更新

# インタラクティブモード
openspec show                  # 選択を促す
openspec validate              # 一括検証モード

# デバッグ
openspec show [change] --json --deltas-only
openspec validate [change] --strict
```

### コマンドフラグ

- `--json` - 機械可読出力
- `--type change|spec` - アイテムの曖昧さを解消
- `--strict` - 包括的な検証
- `--no-interactive` - プロンプトを無効化
- `--skip-specs` - スペック更新なしでアーカイブ
- `--yes`/`-y` - 確認プロンプトをスキップ（非対話アーカイブ）

## ディレクトリ構造

```
openspec/
├── project.md              # プロジェクト規約
├── specs/                  # 現在の真実 - 構築済みのもの
│   └── [capability]/       # 単一の焦点を当てた機能
│       ├── spec.md         # 要件とシナリオ
│       └── design.md       # 技術パターン
├── changes/                # 提案 - 変更すべきもの
│   ├── [change-name]/
│   │   ├── proposal.md     # なぜ、何を、影響
│   │   ├── tasks.md        # 実装チェックリスト
│   │   ├── design.md       # 技術的決定（オプション；基準を参照）
│   │   └── specs/          # デルタ変更
│   │       └── [capability]/
│   │           └── spec.md # ADDED/MODIFIED/REMOVED
│   └── archive/            # 完了した変更
```

## 変更提案の作成

### 決定ツリー

```
新しいリクエスト？
├─ スペックの動作を復元するバグ修正？ → 直接修正
├─ タイポ/フォーマット/コメント？ → 直接修正
├─ 新機能/機能追加？ → 提案を作成
├─ 破壊的変更？ → 提案を作成
├─ アーキテクチャ変更？ → 提案を作成
└─ 不明？ → 提案を作成（より安全）
```

### 提案の構造

1. **ディレクトリを作成:** `changes/[change-id]/`（ケバブケース、動詞で始まる、一意）

2. **proposal.mdを記述:**
```markdown
# Change: [変更の簡単な説明]

## Why
[問題/機会についての1〜2文]

## What Changes
- [変更の箇条書き]
- [破壊的変更は**BREAKING**でマーク]

## Impact
- Affected specs: [機能のリスト]
- Affected code: [主要なファイル/システム]
```

3. **スペックデルタを作成:** `specs/[capability]/spec.md`
```markdown
## ADDED Requirements
### Requirement: New Feature
The system SHALL provide...

#### Scenario: Success case
- **WHEN** user performs action
- **THEN** expected result

## MODIFIED Requirements
### Requirement: Existing Feature
[完全な変更後の要件]

## REMOVED Requirements
### Requirement: Old Feature
**Reason**: [削除理由]
**Migration**: [対処方法]
```
複数の機能が影響を受ける場合は、`changes/[change-id]/specs/<capability>/spec.md`の下に複数のデルタファイルを作成—機能ごとに1つ。

4. **tasks.mdを作成:**
```markdown
## 1. Implementation
- [ ] 1.1 Create database schema
- [ ] 1.2 Implement API endpoint
- [ ] 1.3 Add frontend component
- [ ] 1.4 Write tests
```

5. **必要に応じてdesign.mdを作成:**
以下のいずれかに該当する場合は`design.md`を作成；それ以外は省略:
- 横断的な変更（複数のサービス/モジュール）または新しいアーキテクチャパターン
- 新しい外部依存関係または大幅なデータモデル変更
- セキュリティ、パフォーマンス、または移行の複雑さ
- コーディング前に技術的決定が必要な曖昧さ

最小限の`design.md`スケルトン:
```markdown
## Context
[背景、制約、ステークホルダー]

## Goals / Non-Goals
- Goals: [...]
- Non-Goals: [...]

## Decisions
- Decision: [何をなぜ]
- Alternatives considered: [オプション + 理由]

## Risks / Trade-offs
- [リスク] → 緩和策

## Migration Plan
[手順、ロールバック]

## Open Questions
- [...]
```

## スペックファイル形式

### 重要: シナリオのフォーマット

**正しい**（####ヘッダーを使用）:
```markdown
#### Scenario: User login success
- **WHEN** valid credentials provided
- **THEN** return JWT token
```

**間違い**（箇条書きや太字を使用しない）:
```markdown
- **Scenario: User login**  ❌
**Scenario**: User login     ❌
### Scenario: User login      ❌
```

すべての要件には少なくとも1つのシナリオが必須。

### 要件の表現
- 規範的要件にはSHALL/MUSTを使用（意図的に非規範的でない限りshould/mayは避ける）

### デルタ操作

- `## ADDED Requirements` - 新しい機能
- `## MODIFIED Requirements` - 変更された動作
- `## REMOVED Requirements` - 非推奨の機能
- `## RENAMED Requirements` - 名前の変更

ヘッダーは`trim(header)`でマッチ - 空白は無視。

#### ADDEDとMODIFIEDの使い分け
- ADDED: 単独で要件として成り立つ新しい機能またはサブ機能を導入。既存の要件のセマンティクスを変更するのではなく、直交する変更（例：「スラッシュコマンド設定」の追加）の場合はADDEDを優先。
- MODIFIED: 既存の要件の動作、スコープ、または受け入れ基準を変更。常に完全な更新された要件内容（ヘッダー + すべてのシナリオ）を貼り付ける。アーカイバはここで提供されたもので要件全体を置き換える；部分的なデルタは以前の詳細を失う。
- RENAMED: 名前のみが変更される場合に使用。動作も変更する場合は、RENAMED（名前）とMODIFIED（内容）を新しい名前を参照して使用。

よくある落とし穴: MODIFIEDを使用して以前のテキストを含めずに新しい懸念を追加。これはアーカイブ時に詳細が失われる原因となる。既存の要件を明示的に変更していない場合は、代わりにADDEDの下に新しい要件を追加。

MODIFIEDの要件を正しく記述する方法:
1) `openspec/specs/<capability>/spec.md`で既存の要件を見つける。
2) 要件ブロック全体（`### Requirement: ...`からそのシナリオまで）をコピー。
3) `## MODIFIED Requirements`の下に貼り付け、新しい動作を反映するように編集。
4) ヘッダーテキストが正確に一致すること（空白は無視）を確認し、少なくとも1つの`#### Scenario:`を保持。

RENAMEDの例:
```markdown
## RENAMED Requirements
- FROM: `### Requirement: Login`
- TO: `### Requirement: User Authentication`
```

## トラブルシューティング

### よくあるエラー

**「Change must have at least one delta」**
- `changes/[name]/specs/`が.mdファイル付きで存在するか確認
- ファイルに操作プレフィックス（## ADDED Requirements）があるか確認

**「Requirement must have at least one scenario」**
- シナリオが`#### Scenario:`形式（4つのハッシュ）を使用しているか確認
- シナリオヘッダーに箇条書きや太字を使用しない

**シナリオパースの静かな失敗**
- 正確な形式が必要: `#### Scenario: Name`
- デバッグ: `openspec show [change] --json --deltas-only`

### 検証のヒント

```bash
# 包括的なチェックには常にstrictモードを使用
openspec validate [change] --strict

# デルタパースのデバッグ
openspec show [change] --json | jq '.deltas'

# 特定の要件を確認
openspec show [spec] --json -r 1
```

## ハッピーパススクリプト

```bash
# 1) 現在の状態を確認
openspec spec list --long
openspec list
# オプションの全文検索:
# rg -n "Requirement:|Scenario:" openspec/specs
# rg -n "^#|Requirement:" openspec/changes

# 2) change idを選択してスキャフォールド
CHANGE=add-two-factor-auth
mkdir -p openspec/changes/$CHANGE/{specs/auth}
printf "## Why\n...\n\n## What Changes\n- ...\n\n## Impact\n- ...\n" > openspec/changes/$CHANGE/proposal.md
printf "## 1. Implementation\n- [ ] 1.1 ...\n" > openspec/changes/$CHANGE/tasks.md

# 3) デルタを追加（例）
cat > openspec/changes/$CHANGE/specs/auth/spec.md << 'EOF'
## ADDED Requirements
### Requirement: Two-Factor Authentication
Users MUST provide a second factor during login.

#### Scenario: OTP required
- **WHEN** valid credentials are provided
- **THEN** an OTP challenge is required
EOF

# 4) 検証
openspec validate $CHANGE --strict
```

## 複数機能の例

```
openspec/changes/add-2fa-notify/
├── proposal.md
├── tasks.md
└── specs/
    ├── auth/
    │   └── spec.md   # ADDED: Two-Factor Authentication
    └── notifications/
        └── spec.md   # ADDED: OTP email notification
```

auth/spec.md
```markdown
## ADDED Requirements
### Requirement: Two-Factor Authentication
...
```

notifications/spec.md
```markdown
## ADDED Requirements
### Requirement: OTP Email Notification
...
```

## ベストプラクティス

### シンプルさ優先
- デフォルトで新しいコードは100行未満
- 不十分と証明されるまで単一ファイル実装
- 明確な正当性なしにフレームワークを避ける
- 実績のあるパターンを選択

### 複雑さのトリガー
以下の場合のみ複雑さを追加:
- 現在のソリューションが遅すぎることを示すパフォーマンスデータ
- 具体的なスケール要件（1000人以上のユーザー、100MB以上のデータ）
- 抽象化を必要とする複数の実証済みユースケース

### 明確な参照
- コードの場所には`file.ts:42`形式を使用
- スペックを`specs/auth/spec.md`として参照
- 関連する変更とPRをリンク

### 機能の命名
- 動詞-名詞を使用: `user-auth`、`payment-capture`
- 機能ごとに単一の目的
- 10分で理解できるルール
- 説明に「AND」が必要な場合は分割

### Change IDの命名
- ケバブケース、短く説明的: `add-two-factor-auth`
- 動詞で始まるプレフィックスを優先: `add-`、`update-`、`remove-`、`refactor-`
- 一意性を確保；取られている場合は`-2`、`-3`などを追加

## ツール選択ガイド

| タスク | ツール | 理由 |
|------|------|-----|
| パターンでファイルを検索 | Glob | 高速なパターンマッチング |
| コード内容を検索 | Grep | 最適化された正規表現検索 |
| 特定のファイルを読む | Read | 直接ファイルアクセス |
| 不明なスコープを探索 | Task | 複数ステップの調査 |

## エラーリカバリー

### 変更の競合
1. `openspec list`を実行してアクティブな変更を確認
2. 重複するスペックを確認
3. 変更のオーナーと調整
4. 提案の統合を検討

### 検証失敗
1. `--strict`フラグで実行
2. JSON出力で詳細を確認
3. スペックファイル形式を検証
4. シナリオが適切にフォーマットされているか確認

### コンテキスト不足
1. まずproject.mdを読む
2. 関連スペックを確認
3. 最近のアーカイブを確認
4. 明確化を求める

## クイックリファレンス

### ステージインジケーター
- `changes/` - 提案済み、未構築
- `specs/` - 構築済みでデプロイ済み
- `archive/` - 完了した変更

### ファイルの目的
- `proposal.md` - なぜと何を
- `tasks.md` - 実装手順
- `design.md` - 技術的決定
- `spec.md` - 要件と動作

### CLI基本
```bash
openspec list              # 進行中のものは？
openspec show [item]       # 詳細を表示
openspec validate --strict # 正しいか？
openspec archive <change-id> [--yes|-y]  # 完了をマーク（自動化には--yesを追加）
```

覚えておくこと: スペックは真実。変更は提案。同期を保つ。
