# AWS本番環境構築タスク（Terraform）

## 構成

```
[CloudFront] → [S3] (フロントエンド)
      ↓
[ALB] → [ECS Fargate] (バックエンド)
              ↓
         [RDS PostgreSQL]
```

---

## Phase 1: Terraform準備

- [ ] Terraformプロジェクト構成作成（`infrastructure/`ディレクトリ）
- [ ] tfstateのリモート管理設定（S3 + DynamoDB）
- [ ] 環境別変数ファイル作成（dev/prod）

---

## Phase 2: Terraformでインフラ構築

### 2.1 ネットワーク（`network.tf`）
- [ ] VPC
- [ ] パブリック/プライベートサブネット（2AZ）
- [ ] インターネットゲートウェイ
- [ ] NATゲートウェイ
- [ ] ルートテーブル

### 2.2 セキュリティ（`security.tf`）
- [ ] ALB用セキュリティグループ（80/443）
- [ ] ECS用セキュリティグループ（8000）
- [ ] RDS用セキュリティグループ（5432）

### 2.3 データベース（`rds.tf`）
- [ ] DBサブネットグループ
- [ ] RDS PostgreSQLインスタンス
- [ ] パラメータグループ

### 2.4 コンテナ（`ecs.tf`）
- [ ] ECRリポジトリ
- [ ] ECSクラスター
- [ ] タスク定義
- [ ] ECSサービス
- [ ] IAMロール（タスク実行用）

### 2.5 ロードバランサー（`alb.tf`）
- [ ] ALB
- [ ] ターゲットグループ
- [ ] リスナー

### 2.6 フロントエンド（`frontend.tf`）
- [ ] S3バケット
- [ ] CloudFrontディストリビューション
- [ ] オリジンアクセスコントロール

### 2.7 シークレット（`secrets.tf`）
- [ ] Secrets Manager or Parameter Store
- [ ] DB認証情報
- [ ] アプリケーション設定

---

## Phase 3: アプリケーション対応

### 3.1 バックエンド
- [ ] 本番用Dockerfile作成
- [ ] CORS設定更新
- [ ] 環境変数のSecrets Manager対応

### 3.2 フロントエンド
- [ ] 本番用ビルド設定
- [ ] API URLの環境変数化

### 3.3 データベース
- [ ] Alembicマイグレーション実行手順

---

## Phase 4: CI/CD（GitHub Actions）

- [ ] バックエンドデプロイワークフロー
- [ ] フロントエンドデプロイワークフロー
- [ ] GitHub Secrets設定

---

## Phase 5: 運用設定

- [ ] CloudWatch Logs設定
- [ ] RDS自動バックアップ確認
- [ ] アラーム設定（任意）

---

## 推定コスト（月額 ~$60）

| サービス | 月額目安 |
|----------|----------|
| ECS Fargate | ~$10 |
| RDS PostgreSQL | ~$15 |
| ALB | ~$20 |
| S3 + CloudFront | ~$3 |
| その他 | ~$10 |
