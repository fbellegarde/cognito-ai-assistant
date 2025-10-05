# -----------------------------------------------------------------
# 0. Data Sources (Fetch existing VPC and Subnets)
# -----------------------------------------------------------------
data "aws_vpc" "selected" {
  id = "vpc-04da03db4c6515f69" # Your provided VPC ID
}

data "aws_subnets" "selected" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

# -----------------------------------------------------------------
# 1. AWS CloudWatch Log Group
# -----------------------------------------------------------------
resource "aws_cloudwatch_log_group" "cognito_log_group" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = 7
}

# -----------------------------------------------------------------
# 2. AWS ECR Repository
# -----------------------------------------------------------------
resource "aws_ecr_repository" "cognito_repo" {
  name                 = var.app_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# -----------------------------------------------------------------
# 3. AWS ECS Cluster
# -----------------------------------------------------------------
resource "aws_ecs_cluster" "cognito_cluster" {
  name = "${var.app_name}-cluster"
}

# -----------------------------------------------------------------
# 4. AWS IAM Role (ECS Execution Role)
# -----------------------------------------------------------------
resource "aws_iam_role" "ecs_execution_role" {
  name               = "${var.app_name}-ecs-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Sid = ""
    }]
  })
}

# -----------------------------------------------------------------
# 5. AWS IAM Role Policy Attachment (for Execution Role)
# -----------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "ecs_execution_role_attachment" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# -----------------------------------------------------------------
# 6. AWS IAM Role (ECS Task Role)
# -----------------------------------------------------------------
resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.app_name}-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Sid = ""
    }]
  })
}

# -----------------------------------------------------------------
# 7. AWS IAM Role Policy (Inline Policy for Task Role)
# Enables access to Secrets Manager for DB credentials
# -----------------------------------------------------------------
resource "aws_iam_role_policy" "ecs_task_secrets_policy" {
  name = "SecretsManagerAccess"
  role = aws_iam_role.ecs_task_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = [
        "secretsmanager:GetSecretValue",
        # KMS:Decrypt is often required if the secret is encrypted with a custom key, keep it for safety
        "kms:Decrypt",
      ],
      Resource = [
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:cognito/rds/credentials-*" # Only access the specific secret
      ]
    }]
  })
}

# -----------------------------------------------------------------
# 8. AWS DB Subnet Group (Required for RDS)
# -----------------------------------------------------------------
resource "aws_db_subnet_group" "cognito_db_subnet_group" {
  name       = "${var.app_name}-dbsg"
  subnet_ids = data.aws_subnets.selected.ids
  tags = {
    Name = "${var.app_name}-dbsg"
  }
}

# -----------------------------------------------------------------
# 9. AWS RDS Instance (Configured with your manual settings)
# FIX: engine_version set to "15" and db_name set to "cognito_ai"
# -----------------------------------------------------------------
resource "aws_db_instance" "cognito_rds" {
  identifier             = "cognito-db"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15"                 # <-- FIX: Changed to major version "15"
  instance_class         = "db.t3.micro"
  db_name                = "cognito_ai"         # <-- FIX: Set to match the DB name inferred from the previous state
  username               = "postgresadmin"
  password               = var.rds_password
  
  # VPC and Connectivity settings
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.cognito_db_subnet_group.name
  publicly_accessible    = false

  # Dev/Test/Free Tier settings
  skip_final_snapshot    = true
  deletion_protection    = false
}

# -----------------------------------------------------------------
# 10. Security Group for RDS (Allows ONLY ECS access to the DB port)
# -----------------------------------------------------------------
resource "aws_security_group" "rds_sg" {
  name        = "cognito-ai-db-sg-tf"
  description = "Allow inbound traffic from ECS containers"
  vpc_id      = data.aws_vpc.selected.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    # Allow inbound traffic ONLY from the ECS Security Group
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# -----------------------------------------------------------------
# 11. Security Group for ECS (Allows inbound HTTP traffic)
# -----------------------------------------------------------------
resource "aws_security_group" "ecs_sg" {
  name        = "${var.app_name}-ecs-sg"
  description = "Allow inbound HTTP/8000 traffic to ECS tasks"
  vpc_id      = data.aws_vpc.selected.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # WARNING: In production, limit this!
  }

  # Allow all outbound traffic (Needed to reach RDS and the Internet for the app/API)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# -----------------------------------------------------------------
# 12. AWS ECS Task Definition
# Uses Secrets Manager for database configuration
# -----------------------------------------------------------------
resource "aws_ecs_task_definition" "cognito_task" {
  family                   = "${var.app_name}-task"
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.app_name}-app"
      image     = "${aws_ecr_repository.cognito_repo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.cognito_log_group.name,
          "awslogs-region"        = var.aws_region,
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        {
          name  = "DJANGO_SETTINGS_MODULE",
          value = "cognito_ai_assistant.settings"
        },
        {
          name  = "DB_HOST",
          value = "cognito-db.c6vo2mww088d.${var.aws_region}.rds.amazonaws.com" # Your DB Endpoint
        },
        {
          name  = "DB_NAME",
          value = "cognito_ai" # <-- MATCHES DB NAME ABOVE
        },
        {
          name  = "DB_PORT",
          value = "5432"
        },
        {
          name  = "DB_USER",
          value = "postgresadmin"
        }
      ]
      secrets = [
        {
          name      = "DB_PASSWORD",
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:cognito/rds/credentials-fZK97G:password::" # Target the 'password' key
        }
      ]
    }
  ])
}

# -----------------------------------------------------------------
# 13. ECS Fargate Service (Runs the container)
# -----------------------------------------------------------------
resource "aws_ecs_service" "cognito_service" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.cognito_cluster.id
  task_definition = aws_ecs_task_definition.cognito_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups = [aws_security_group.ecs_sg.id]
    subnets         = data.aws_subnets.selected.ids
    assign_public_ip = true
  }
}

# -----------------------------------------------------------------
# 14. Outputs
# -----------------------------------------------------------------
output "ecr_repository_url" {
  description = "The ECR repository URL for pushing the Docker image"
  value       = aws_ecr_repository.cognito_repo.repository_url
}