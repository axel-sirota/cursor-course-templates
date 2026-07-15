variable "project" {
  type        = string
  description = "Project name, used in the <project>-<env>-<resource> naming convention"
  default     = "acme"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
  default     = "dev"
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

# --- Networking ---

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid CIDR block."
  }
}

variable "availability_zone_count" {
  type        = number
  description = "Number of AZs to spread subnets across"
  default     = 2
  validation {
    condition     = var.availability_zone_count >= 2 && var.availability_zone_count <= 4
    error_message = "availability_zone_count must be between 2 and 4."
  }
}

variable "single_nat_gateway" {
  type        = bool
  description = "Use one shared NAT gateway (cheaper, dev) instead of one per AZ (HA, prod)"
  default     = true
}

# --- ALB / TLS ---

variable "acm_certificate_arn" {
  type        = string
  description = "ARN of an ACM certificate covering the ALB's domain, for the HTTPS listener"
}

# --- ECS Service ---

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

variable "enable_autoscaling" {
  type        = bool
  description = "Whether to attach Application Auto Scaling to the ECS service"
  default     = false
}

# --- Static Site ---

variable "static_site_domain" {
  type        = string
  description = "Domain name for the CloudFront distribution (informational tag only in this example — no Route53 wiring included)"
  default     = "static.example.com"
}
