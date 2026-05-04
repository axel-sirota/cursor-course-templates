variable "vpc_cidr" {
  description = "CIDR block for the VPC. Must be a valid IPv4 CIDR, e.g. '10.0.0.0/16'."
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "environment" {
  description = "Deployment environment name (dev, staging, prod). Used for resource naming and tagging."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "project" {
  description = "Project or product name. Used for resource naming and the Project tag."
  type        = string
}

variable "tags" {
  description = "Additional tags to merge with the module's common tags. Key-value string pairs."
  type        = map(string)
  default     = {}
}
