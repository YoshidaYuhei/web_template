terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # tfstate をリモート管理する場合はコメントを外す
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "web-template/terraform.tfstate"
  #   region         = "ap-northeast-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
