# ─────────────────────────────────────────────────────────────────────────────
# variables.tf – C22 Mastery Quiz Tool
# ─────────────────────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"
}

variable "app_name" {
  description = "Short identifier used in all resource names"
  type        = string
  default     = "c22-mastery-quiz-tool"
}

variable "ecr_repo_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "c22-mastery-quiz-tool"
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "c22-mastery-quiz-cluster"
}

variable "ecs_service_name" {
  description = "Name of the ECS service"
  type        = string
  default     = "c22-mastery-quiz-service"
}

variable "ecs_task_family" {
  description = "Task definition family name"
  type        = string
  default     = "c22-mastery-quiz-task"
}

variable "container_name" {
  description = "Name of the container inside the task definition"
  type        = string
  default     = "c22-mastery-quiz-app"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "cpu" {
  description = "Fargate task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "image_tag" {
  description = "Docker image tag to deploy (set to 'latest' or a git SHA)"
  type        = string
  default     = "latest"
}

variable "vpc_id" {
  description = "ID of your existing VPC (e.g. vpc-0abc1234)"
  type        = string
}

variable "subnet_ids" {
  description = "List of existing public subnet IDs to deploy into (minimum 2 for ALB, must be in different AZs)"
  type        = list(string)
}

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "C22-Mastery-Quiz-Tool"
    ManagedBy   = "Terraform"
    Environment = "production"
  }
}
