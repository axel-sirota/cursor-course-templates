variable "project" {
  type        = string
  description = "Project name, used in the <project>-<env>-<resource> naming convention"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
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

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
}
