# D:\cognito_ai_assistant\IaC\terraform\variables.tf
variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "cognito-ai"
}