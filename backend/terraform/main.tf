provider "aws" {
  region = "us-east-1"
}

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
  identifier                  = "palind-db"
  allocated_storage           = 10
  engine                      = "postgres"
  engine_version              = "15.3"
  instance_class              = "db.t3.micro"
  username                    = "postgres"
  manage_master_user_password = true
  publicly_accessible         = true # Only in dev?
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
    name = "availability-zone-id"
    values = ["use1-az1", "use1-az2", "use1-az6"]
  }
}

resource "aws_apprunner_vpc_connector" "django" {
  vpc_connector_name = "django"
  # Subnets that support App Runner
  subnets         = data.aws_subnets.selected.ids
  security_groups = data.aws_security_groups.selected.ids
}

resource "aws_apprunner_service" "django_tf" {
  service_name = "django_tf"

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
      repository_url   = "https://github.com/curesdev/palind"
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

