# ─────────────────────────────────────────────────────────────────────────────
# outputs.tf – C22 Mastery Quiz Tool
# ─────────────────────────────────────────────────────────────────────────────

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer — open this in your browser"
  value       = aws_lb.app.dns_name
}

output "app_url" {
  description = "Full HTTP URL of the deployed app"
  value       = "http://${aws_lb.app.dns_name}"
}

output "ecr_repository_url" {
  description = "ECR repository URL — use this in deploy.sh"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.app.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for container logs"
  value       = aws_cloudwatch_log_group.app.name
}

output "vpc_id" {
  description = "VPC ID in use"
  value       = data.aws_vpc.main.id
}
