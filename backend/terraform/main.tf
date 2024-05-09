provider "aws" {
  region = "us-east-1"
}

# Variables

variable "parent_domain_zone_id" {
  default = "Z01915732ZBZKC8D32TPT"
}

variable "domain_name" {
  default = "app.palind.io"
}

variable "environment" {
  default = "prod"
}

# Backend

terraform {
  backend "s3" {
    bucket = "palind-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_s3_bucket" "bucket_terraform_state" {
  #bucket = "palind-terraform-state-${var.environment}"
  bucket = "palind-terraform-state"
}

# S3

# Secrets

data "aws_secretsmanager_random_password" "django_secret_key" {
  password_length = 100
}

resource "aws_secretsmanager_secret" "django_secret_key" {
  name = "django_secret_key"
}

resource "aws_secretsmanager_secret_version" "django_secret_key" {
  secret_id     = aws_secretsmanager_secret.django_secret_key.id
  secret_string = data.aws_secretsmanager_random_password.django_secret_key.random_password
  lifecycle {
    ignore_changes = [secret_string, ]
  }
}


# IAM

resource "aws_iam_role_policy" "get_secrets" {
  name = "get_secrets_policy"
  role = aws_iam_role.get_secrets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "secretsmanager:GetSecretValue"
        Resource = aws_db_instance.default.master_user_secret[0].secret_arn
      },
      {
        Effect   = "Allow"
        Action   = "secretsmanager:GetSecretValue"
        Resource = aws_secretsmanager_secret.django_secret_key.arn
      }
    ]
  })
}


resource "aws_iam_role" "get_secrets" {
  name = "get_secrets_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service : "tasks.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

# RDS

resource "aws_db_instance" "default" {
  allocated_storage           = 10
  engine                      = "postgres"
  engine_version              = "15.3"
  instance_class              = "db.t3.micro"
  username                    = "postgres"
  manage_master_user_password = true
  publicly_accessible         = var.environment == "dev" ? true : false
  storage_encrypted           = true
}

# Retrieve Subnets and Security Group

data "aws_vpc" "default" {
  default = true
}

data "aws_security_groups" "selected" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# App runner

resource "aws_apprunner_connection" "django" {
  connection_name = "django"
  provider_type   = "GITHUB"
}

data "aws_subnets" "selected" {
  filter {
    name   = "availability-zone-id"
    values = ["use1-az1", "use1-az2", "use1-az6"]
  }
}

resource "aws_apprunner_vpc_connector" "django" {
  vpc_connector_name = "django"
  # Subnets that support App Runner
  subnets         = data.aws_subnets.selected.ids
  security_groups = data.aws_security_groups.selected.ids
}

resource "aws_apprunner_service" "django" {
  service_name = "django"

  instance_configuration {
    cpu               = "512"
    memory            = "1024"
    instance_role_arn = aws_iam_role.get_secrets.arn
  }

  source_configuration {
    auto_deployments_enabled = true

    authentication_configuration {
      connection_arn = aws_apprunner_connection.django.arn
    }

    code_repository {
      repository_url   = "https://github.com/RareCamp/palind"
      source_directory = "/backend"

      code_configuration {
        code_configuration_values {
          build_command = "pip install -r requirements.txt"
          port          = "8000"
          runtime       = "PYTHON_3"
          start_command = "sh startup.sh"
          runtime_environment_secrets = {
            DJANGO_SECRET_KEY       = aws_secretsmanager_secret_version.django_secret_key.arn
            DJANGO_DB_USER_PASSWORD = aws_db_instance.default.master_user_secret[0].secret_arn
          }
          runtime_environment_variables = {
            DJANGO_DB_HOST = aws_db_instance.default.address
            DJANGO_DB_PORT = aws_db_instance.default.port
            DJANGO_DB_NAME = aws_db_instance.default.db_name
          }
        }
        configuration_source = "API"
      }

      source_code_version {
        type  = "BRANCH"
        value = "master"
      }
    }
  }

  network_configuration {
    ingress_configuration {
      is_publicly_accessible = true
    }

    egress_configuration {
      egress_type       = "VPC"
      vpc_connector_arn = aws_apprunner_vpc_connector.django.arn
    }
  }
}

resource "aws_apprunner_custom_domain_association" "app_domain" {
  domain_name          = var.domain_name
  service_arn          = aws_apprunner_service.django.arn
  enable_www_subdomain = false
}

# Route53

resource "aws_route53_zone" "app_domain" {
  name = var.domain_name
}

resource "aws_route53_record" "validation_records_linglinger_1" {
  name    = tolist(aws_apprunner_custom_domain_association.app_domain.certificate_validation_records)[0].name
  type    = tolist(aws_apprunner_custom_domain_association.app_domain.certificate_validation_records)[0].type
  records = [tolist(aws_apprunner_custom_domain_association.app_domain.certificate_validation_records)[0].value]
  ttl     = 300
  zone_id = aws_route53_zone.app_domain.id
}

resource "aws_route53_record" "validation_records_linglinger_2" {
  name    = tolist(aws_apprunner_custom_domain_association.app_domain.certificate_validation_records)[1].name
  type    = tolist(aws_apprunner_custom_domain_association.app_domain.certificate_validation_records)[1].type
  records = [tolist(aws_apprunner_custom_domain_association.app_domain.certificate_validation_records)[1].value]
  ttl     = 300
  zone_id = aws_route53_zone.app_domain.id
}

resource "aws_route53_record" "custom_domain" {
  name    = var.domain_name
  type    = "A"
  zone_id = aws_route53_zone.app_domain.id

  alias {
    evaluate_target_health = true
    name                   = aws_apprunner_service.django.service_url
    zone_id                = var.parent_domain_zone_id
  }
}
