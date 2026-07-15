output "alb_security_group_id" {
  description = "Security group ID of the ALB, consumed by modules/ecs-service to allow ingress"
  value       = aws_security_group.alb.id
}

output "target_group_arn" {
  description = "ARN of the target group, consumed by modules/ecs-service's load_balancer block"
  value       = aws_lb_target_group.web.arn
}

output "alb_dns_name" {
  description = "Public DNS name of the ALB"
  value       = aws_lb.this.dns_name
}

output "alb_arn" {
  description = "ARN of the ALB"
  value       = aws_lb.this.arn
}
