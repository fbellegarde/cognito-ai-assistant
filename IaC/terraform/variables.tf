variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "Your AWS Account ID (for ARN construction)"
  type        = string
  # IMPORTANT: Replace this with your actual AWS account ID
  # The ARN provided indicates this is 331248921225
  default     = "331248921225" 
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "cognito-ai"
}

variable "rds_password" {
  description = "The secret password for the RDS database (only needed for the aws_db_instance resource)."
  type        = string
  sensitive   = true
}