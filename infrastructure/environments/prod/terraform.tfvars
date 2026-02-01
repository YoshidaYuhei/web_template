project_name = "web-template"
environment  = "prod"
aws_region   = "ap-northeast-1"

# Database
db_instance_class = "db.t4g.small"
db_name           = "web_template"
db_username       = "admin"
# 本番では TF_VAR_db_password 環境変数で渡す
db_password       = ""

# ECS
ecs_cpu    = 512
ecs_memory = 1024

# Secrets (本番では環境変数 TF_VAR_xxx で渡す)
secret_key     = ""
openai_api_key = ""
