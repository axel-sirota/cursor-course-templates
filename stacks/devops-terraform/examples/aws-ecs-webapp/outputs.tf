output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets (ECS task placement)"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "IDs of the public subnets (ALB placement)"
  value       = module.vpc.public_subnet_ids
}

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster, used by scripts/verify_deployment.py"
  value       = module.ecs_service.cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service, used by scripts/verify_deployment.py"
  value       = module.ecs_service.service_name
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name for the static frontend"
  value       = module.static_site.cloudfront_domain_name
}
