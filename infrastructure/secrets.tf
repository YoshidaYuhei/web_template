# Secrets Manager for sensitive values
resource "aws_secretsmanager_secret" "app_secrets" {
  name = "${var.project_name}-${var.environment}-app-secrets"

  tags = {
    Name = "${var.project_name}-${var.environment}-app-secrets"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id

  secret_string = jsonencode({
    DB_PASSWORD    = var.db_password
    SECRET_KEY     = var.secret_key
    OPENAI_API_KEY = var.openai_api_key
  })
}

# IAM Policy for ECS to access Secrets Manager
resource "aws_iam_policy" "ecs_secrets_access" {
  name        = "${var.project_name}-${var.environment}-ecs-secrets-policy"
  description = "Allow ECS tasks to access Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.app_secrets.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_access" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.ecs_secrets_access.arn
}
