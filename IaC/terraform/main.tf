# -----------------------------------------------------------------
# 1. AWS CloudWatch Log Group
# -----------------------------------------------------------------
resource "aws_cloudwatch_log_group" "cognito_log_group" {
  name              = "/ecs/cognito-ai"
  retention_in_days = 7
}

# -----------------------------------------------------------------
# 2. AWS ECR Repository
# -----------------------------------------------------------------
resource "aws_ecr_repository" "cognito_repo" {
  name                 = "cognito-ai"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# -----------------------------------------------------------------
# 3. AWS ECS Cluster
# -----------------------------------------------------------------
resource "aws_ecs_cluster" "cognito_cluster" {
  name = "cognito-ai-cluster"
}

# -----------------------------------------------------------------
# 4. AWS IAM Role (ECS Execution Role)
# FIX: Removing 'managed_policy_arns' and defining attachment separately
# -----------------------------------------------------------------
resource "aws_iam_role" "ecs_execution_role" {
  name               = "cognito-ai-ecs-execution-role"
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
  # The managed_policy_arns argument is REMOVED to resolve the warning
}

# -----------------------------------------------------------------
# 5. AWS IAM Role Policy Attachment (for Execution Role)
# This replaces the deprecated 'managed_policy_arns' block in the role above
# -----------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "ecs_execution_role_attachment" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# -----------------------------------------------------------------
# 6. AWS IAM Role (ECS Task Role)
# The second warning likely referred to a task role with a managed_policy_arn
# Since the plan shows only an inline policy, we'll keep it clean, but ensure
# the inline policy is defined cleanly.
# -----------------------------------------------------------------
resource "aws_iam_role" "ecs_task_role" {
  name               = "cognito-ai-ecs-task-role"
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
# This ensures the application can read secrets/parameters
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
        "kms:Decrypt",
        "ssm:GetParameters" # Added SSM since your CloudFormation had it
      ],
      Resource = "*"
    }]
  })
}

# -----------------------------------------------------------------
# 8. AWS ECS Task Definition
# -----------------------------------------------------------------
resource "aws_ecs_task_definition" "cognito_task" {
  family                   = "cognito-ai-task"
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "cognito-ai-app"
      image     = "${aws_ecr_repository.cognito_repo.repository_url}:latest" # Assumes you push 'latest'
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
          "awslogs-region"        = "us-east-1",
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
          # Add environment variables here as needed (e.g., DJANGO_SETTINGS_MODULE)
      ]
    }
  ])
}