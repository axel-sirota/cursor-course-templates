variable "project" {
  type        = string
  description = "Project name"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
}

variable "aws_region" {
  type        = string
  description = "AWS region, used in the awslogs log configuration"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID the service's security group attaches to"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for ECS task ENIs"
  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "At least 2 private subnets are required for availability across AZs."
  }
}

variable "alb_security_group_id" {
  type        = string
  description = "Security group ID of the ALB, allowed as the only ingress source"
}

variable "target_group_arn" {
  type        = string
  description = "ARN of the ALB target group this service registers into"
}

variable "ecr_repository_url" {
  type        = string
  description = "ECR repository URL for the application image"
}

variable "image_tag" {
  type        = string
  description = "Docker image tag to deploy"
  default     = "latest"
}

variable "container_port" {
  type        = number
  description = "Port the application listens on inside the container"
  default     = 8080
}

variable "task_cpu" {
  type        = number
  description = "Fargate task CPU units"
  default     = 256
  validation {
    condition     = contains([256, 512, 1024, 2048, 4096], var.task_cpu)
    error_message = "task_cpu must be one of the Fargate-supported values: 256, 512, 1024, 2048, 4096."
  }
}

variable "task_memory" {
  type        = number
  description = "Fargate task memory (MiB)"
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

variable "environment_variables" {
  type        = map(string)
  description = "Non-secret environment variables injected into the container"
  default     = {}
}

variable "secret_arns" {
  type        = map(string)
  description = "Map of container env var name -> SSM/Secrets Manager ARN"
  default     = {}
  sensitive   = true
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch Logs retention period"
  default     = 30
}

variable "enable_autoscaling" {
  type        = bool
  description = "Whether to attach Application Auto Scaling to the service"
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
}
