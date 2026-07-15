# ---------------------------------------------------------------------------
# backend-config-template.tf
#
# Copy the relevant blocks into backend.tf / providers.tf at project root.
# The S3 bucket (and, if using the classic DynamoDB pattern, the lock table)
# must already exist — bootstrap them by hand first (see
# rules/000-environment-setup.mdc, section 5).
# ---------------------------------------------------------------------------

# =============================================================================
# Option A (recommended for new projects): S3 backend with native locking
# Requires Terraform >= 1.11 (use_lockfile became GA in 1.11; experimental
# from 1.10). No DynamoDB table needed.
# =============================================================================

terraform {
  backend "s3" {
    # Values below are typically supplied via `-backend-config=backend.hcl`
    # (see backend.hcl.example) rather than hardcoded here, so the same
    # backend.tf works across dev/staging/prod with different config files.
    #
    # bucket       = "acme-terraform-state"
    # key          = "aws-ecs-webapp/terraform.tfstate"
    # region       = "us-east-1"
    # encrypt      = true
    # use_lockfile = true
  }
}

# =============================================================================
# Option B (classic, still fully supported): S3 backend + DynamoDB lock table
# Use this if the team's existing tooling or Terraform version predates 1.11.
# =============================================================================

# terraform {
#   backend "s3" {
#     bucket         = "acme-terraform-state"
#     key            = "aws-ecs-webapp/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     dynamodb_table = "acme-terraform-locks"
#   }
# }

# =============================================================================
# The DynamoDB lock table resource, if using Option B — created ONCE, by
# hand, in a bootstrap step BEFORE this project's own `terraform init`
# (a project cannot create the backend it depends on to store its own state).
# Keep this in a separate, one-time "bootstrap" root module, not in the
# project that uses it.
# =============================================================================

# resource "aws_dynamodb_table" "terraform_locks" {
#   name         = "acme-terraform-locks"
#   billing_mode = "PAY_PER_REQUEST"
#   hash_key     = "LockID"
#
#   attribute {
#     name = "LockID"
#     type = "S"
#   }
#
#   tags = {
#     Project   = "acme"
#     ManagedBy = "terraform-bootstrap"
#   }
# }

# =============================================================================
# providers.tf — provider version pin + default_tags
# =============================================================================

# terraform {
#   required_version = ">= 1.9, < 2.0.0"
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 5.0"
#     }
#   }
# }
#
# provider "aws" {
#   region = var.aws_region
#
#   default_tags {
#     tags = {
#       Project     = var.project
#       Environment = var.environment
#       ManagedBy   = "terraform"
#     }
#   }
# }

# =============================================================================
# backend.hcl.example — partial backend config, passed via
# `terraform init -backend-config=backend.hcl`. One file per environment
# (backend.dev.hcl, backend.staging.hcl, backend.prod.hcl), gitignored if it
# contains anything environment-sensitive (it usually doesn't, but treat it
# like a .tfvars file to be safe).
# =============================================================================

# bucket       = "acme-terraform-state"
# key          = "aws-ecs-webapp/dev/terraform.tfstate"
# region       = "us-east-1"
# encrypt      = true
# use_lockfile = true
