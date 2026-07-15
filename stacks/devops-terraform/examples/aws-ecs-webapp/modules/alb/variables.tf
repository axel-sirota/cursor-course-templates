variable "project" {
  type        = string
  description = "Project name"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID the ALB and target group attach to"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for the ALB"
  validation {
    condition     = length(var.public_subnet_ids) >= 2
    error_message = "At least 2 public subnets are required for the ALB."
  }
}

variable "container_port" {
  type        = number
  description = "Port the target group forwards traffic to"
  default     = 8080
}

variable "acm_certificate_arn" {
  type        = string
  description = "ARN of an ACM certificate covering the ALB's domain, for the HTTPS listener"
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
}
