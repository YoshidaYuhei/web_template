project_name = "web-template"
environment  = "stg"
aws_region   = "ap-northeast-1"

# Database
db_instance_class = "db.t4g.micro"
db_name           = "web_template"
db_username       = "admin"
db_password       = "change-me-in-production"

# ECS
ecs_cpu    = 256
ecs_memory = 512

# Secrets (本番では環境変数 TF_VAR_xxx で渡す)
secret_key     = "change-me-in-production"
openai_api_key = ""
