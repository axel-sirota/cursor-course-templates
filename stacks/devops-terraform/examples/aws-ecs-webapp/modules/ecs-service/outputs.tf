output "cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.this.arn
}

output "cluster_name" {
  description = "Name of the ECS cluster, used by scripts/verify_deployment.py"
  value       = aws_ecs_cluster.this.name
}

output "service_name" {
  description = "Name of the ECS service, used by scripts/verify_deployment.py"
  value       = aws_ecs_service.web.name
}

output "task_definition_arn" {
  description = "ARN of the current task definition revision"
  value       = aws_ecs_task_definition.web.arn
}

output "service_security_group_id" {
  description = "Security group ID attached to the ECS service ENIs"
  value       = aws_security_group.service.id
}
