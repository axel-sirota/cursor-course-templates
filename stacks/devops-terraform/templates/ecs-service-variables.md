# ECS Service Module: Variables Template

The `variables.tf` contract for `modules/ecs-service` — the Terraform analog of a Pydantic request/response schema. Design this in the architect phase before writing `main.tf`.

## Core Module Variables

```hcl
# modules/ecs-service/variables.tf

variable "project" {
  type        = string
  description = "Project name, used in the <project>-<env>-<resource> naming convention"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  type        = string
  description = "AWS region to deploy into"
  default     = "us-east-1"
}
```

## Networking Inputs (Consumed From `modules/vpc` Outputs)

```hcl
variable "vpc_id" {
  type        = string
  description = "VPC ID the ECS service's security group and target group attach to"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for ECS task ENIs (Fargate awsvpc networking)"
  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "At least 2 private subnets are required for availability across AZs."
  }
}

variable "alb_security_group_id" {
  type        = string
  description = "Security group ID of the ALB, allowed as the only ingress source to the service's security group"
}

variable "target_group_arn" {
  type        = string
  description = "ARN of the ALB target group this service registers into"
}
```

## Container / Task Definition Inputs

```hcl
variable "ecr_repository_url" {
  type        = string
  description = "ECR repository URL for the application image, e.g. 123456789012.dkr.ecr.us-east-1.amazonaws.com/acme-web"
}

variable "image_tag" {
  type        = string
  description = "Docker image tag to deploy, e.g. a Git SHA or semantic version"
  default     = "latest"
}

variable "container_port" {
  type        = number
  description = "Port the application listens on inside the container"
  default     = 8080
}

variable "task_cpu" {
  type        = number
  description = "Fargate task CPU units (256, 512, 1024, 2048, 4096)"
  default     = 256
  validation {
    condition     = contains([256, 512, 1024, 2048, 4096], var.task_cpu)
    error_message = "task_cpu must be one of the Fargate-supported values: 256, 512, 1024, 2048, 4096."
  }
}

variable "task_memory" {
  type        = number
  description = "Fargate task memory (MiB), must be a valid pairing with task_cpu per AWS Fargate sizing table"
  default     = 512
}

variable "desired_count" {
  type        = number
  description = "Number of ECS tasks to run"
  default     = 2
  validation {
    condition     = var.desired_count >= 1 && var.desired_count <= 20
    error_message = "desired_count must be between 1 and 20."
  }
}
```

## Environment / Secrets Inputs

```hcl
variable "environment_variables" {
  type        = map(string)
  description = "Non-secret environment variables injected into the container"
  default     = {}
}

variable "secret_arns" {
  type        = map(string)
  description = "Map of container env var name -> SSM Parameter Store / Secrets Manager ARN, injected via the ECS task definition's `secrets` block"
  default     = {}
  sensitive   = true
}
```

## Observability / Lifecycle Inputs

```hcl
variable "log_retention_days" {
  type        = number
  description = "CloudWatch Logs retention period for the service's log group"
  default     = 30
}

variable "enable_autoscaling" {
  type        = bool
  description = "Whether to attach an Application Auto Scaling target/policy to the service"
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags, merged with local.common_tags"
  default     = {}
}
```

## Module Outputs Contract

```hcl
# modules/ecs-service/outputs.tf

output "cluster_arn" {
  description = "ARN of the ECS cluster, consumed by CI/CD deploy scripts and post-apply verification"
  value       = aws_ecs_cluster.this.arn
}

output "cluster_name" {
  description = "Name of the ECS cluster, used by scripts/verify_deployment.py"
  value       = aws_ecs_cluster.this.name
}

output "service_name" {
  description = "Name of the ECS service, used by scripts/verify_deployment.py and post-apply checks"
  value       = aws_ecs_service.web.name
}

output "task_definition_arn" {
  description = "ARN of the current task definition revision"
  value       = aws_ecs_task_definition.web.arn
}

output "service_security_group_id" {
  description = "Security group ID attached to the ECS service ENIs, for cross-module reference (e.g. RDS ingress rule)"
  value       = aws_security_group.service.id
}
```

This mirrors the reference stack's Pydantic layered-model pattern (`Base` / full / `Create` / `Update`) conceptually: `variables.tf` is the "input contract" (what callers must provide, analogous to a `*Create` model) and `outputs.tf` is the "response contract" (what the module exposes back, analogous to a `*Response` model).
