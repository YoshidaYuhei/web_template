# スケーリングガイド

規模拡大時にコストをかけてでも対応すべき項目をまとめています。

---

## 優先度: 高（ユーザー影響大）

### 1. ECS タスク数の増加
**現状:** 1タスク
**推奨:** 2タスク以上

| 指標 | 対応タイミング |
|------|---------------|
| CPU使用率 | 常時70%超 |
| レスポンス遅延 | P95が500ms超 |
| エラー率 | 1%超 |

```hcl
# ecs.tf
resource "aws_ecs_service" "app" {
  desired_count = 2  # 1 → 2以上
}
```

**コスト増:** 約$10/月（1タスク追加あたり）

---

### 2. RDS マルチAZ化
**現状:** シングルAZ
**推奨:** マルチAZ

| 指標 | 対応タイミング |
|------|---------------|
| SLA要件 | 99.9%以上必要 |
| ダウンタイム許容 | 数分も許容不可 |

```hcl
# rds.tf
resource "aws_db_instance" "main" {
  multi_az = true
}
```

**コスト増:** 約2倍（RDS料金）

---

### 3. RDS インスタンスサイズ増強
**現状:** db.t4g.micro
**推奨:** 負荷に応じて段階的に

| インスタンス | 用途 | 月額目安 |
|-------------|------|----------|
| db.t4g.micro | 開発/小規模 | ~$15 |
| db.t4g.small | 小〜中規模 | ~$30 |
| db.t4g.medium | 中規模 | ~$60 |
| db.r6g.large | 大規模/高負荷 | ~$150 |

| 指標 | 対応タイミング |
|------|---------------|
| CPU使用率 | 常時80%超 |
| 接続数 | 上限の80%超 |
| スロークエリ | 頻発 |

---

### 4. NAT Gateway の冗長化
**現状:** 1AZに1つ
**推奨:** 各AZに1つ

| 指標 | 対応タイミング |
|------|---------------|
| 可用性要件 | 99.9%以上 |
| AZ障害対策 | 必須 |

```hcl
# network.tf
resource "aws_nat_gateway" "main" {
  count         = length(var.availability_zones)  # 1 → 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
}
```

**コスト増:** 約$35/月（NAT Gateway追加）

---

## 優先度: 中（セキュリティ/運用改善）

### 5. WAF の導入
**現状:** なし
**推奨:** AWS WAF

| 指標 | 対応タイミング |
|------|---------------|
| 攻撃検知 | 不正アクセス増加 |
| コンプライアンス | セキュリティ監査対応 |

```hcl
# waf.tf（新規作成）
resource "aws_wafv2_web_acl" "main" {
  name  = "${var.project_name}-${var.environment}-waf"
  scope = "CLOUDFRONT"
  # ...
}
```

**コスト増:** 約$5/月〜（ルール数/リクエスト数による）

---

### 6. CloudFront 関数 / Lambda@Edge
**現状:** なし
**推奨:** 必要に応じて

| 用途 | 対応タイミング |
|------|---------------|
| A/Bテスト | マーケティング要件 |
| 認証処理 | エッジで認証が必要 |
| リダイレクト | 複雑なURL書き換え |

**コスト増:** リクエスト数による（$0.1/100万リクエスト〜）

---

### 7. RDS リードレプリカ
**現状:** なし
**推奨:** 読み取り負荷が高い場合

| 指標 | 対応タイミング |
|------|---------------|
| 読み取り/書き込み比率 | 10:1以上 |
| レポート/分析クエリ | 本番DBに影響 |

```hcl
# rds.tf
resource "aws_db_instance" "replica" {
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = var.db_instance_class
}
```

**コスト増:** 約$15/月〜（レプリカインスタンス）

---

## 優先度: 低（大規模時）

### 8. ECS Auto Scaling
**現状:** 固定タスク数
**推奨:** 負荷に応じた自動スケール

```hcl
# ecs.tf
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}
```

**コスト増:** スケールしたタスク分

---

### 9. ElastiCache（Redis/Memcached）
**現状:** なし
**推奨:** セッション管理/キャッシュが必要な場合

| 用途 | 対応タイミング |
|------|---------------|
| セッション共有 | ECSタスク2台以上 |
| クエリキャッシュ | DB負荷軽減 |
| レート制限 | API制限が必要 |

**コスト増:** 約$15/月〜（cache.t4g.micro）

---

### 10. Aurora への移行
**現状:** RDS PostgreSQL
**推奨:** 超大規模/高可用性要件

| 指標 | 対応タイミング |
|------|---------------|
| 書き込み性能 | RDSでは不足 |
| 自動スケール | ストレージ自動拡張が必要 |
| フェイルオーバー | 30秒以内が必要 |

**コスト増:** 約1.5〜2倍（RDS比）

---

## スケーリング判断フロー

```
ユーザー増加 / 負荷増加
         ↓
    ┌─────────────────┐
    │ メトリクス確認   │
    │ - CPU使用率      │
    │ - メモリ使用率   │
    │ - レスポンス時間 │
    │ - エラー率       │
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │ ボトルネック特定 │
    └────────┬────────┘
             ↓
     ┌───────┴───────┐
     ↓               ↓
  ECS負荷        DB負荷
     ↓               ↓
 タスク増加     インスタンス
 Auto Scaling    サイズアップ
                リードレプリカ
```

---

## 監視すべきメトリクス

| サービス | メトリクス | 警告閾値 | 危険閾値 |
|----------|-----------|----------|----------|
| ECS | CPU使用率 | 70% | 85% |
| ECS | メモリ使用率 | 70% | 85% |
| RDS | CPU使用率 | 70% | 85% |
| RDS | 接続数 | 80% | 90% |
| RDS | ストレージ空き | 20% | 10% |
| ALB | 5xxエラー率 | 1% | 5% |
| ALB | レスポンス時間 | 500ms | 1000ms |
