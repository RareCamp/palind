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
  #identifier                  = "palind-db"
  allocated_storage           = 10
  engine                      = "postgres"
  engine_version              = "15.3"
  instance_class              = "db.t3.micro"
  username                    = "postgres"
  manage_master_user_password = true
  #storage_encrypted           = true
}

# App runner

resource "aws_apprunner_connection" "django" {
  connection_name = "django"
  provider_type   = "GITHUB"
}

# resource "aws_apprunner_vpc_connector" "django" {
#   vpc_connector_name = "django"
#   subnets = [
#     "subnet-010a14a4f8e29d0fb",
#     "subnet-04223d75069133fc7",
#     "subnet-0b989271de0c9e6bf",
#   ]
#   security_groups = [
#     "sg-0defecd7dd61b6a07",
#   ]
# }

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
      egress_type = "VPC"
      #   vpc_connector_arn = aws_apprunner_vpc_connector.django.arn
      vpc_connector_arn = "arn:aws:apprunner:us-east-1:762786077843:vpcconnector/Default/1/d26e4ddf27bb43d296017b8303aaba92"
    }
  }
}

# EC2 instance to debug

# data "aws_ami" "ubuntu" {
#   most_recent = true
#   filter {
#     name   = "name"
#     values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
#   }
# }

# resource "aws_instance" "debug" {
#   instance_type = "t2.micro"
#   key_name      = "palind_debug"
# }
