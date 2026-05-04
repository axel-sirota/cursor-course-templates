# Terraform Module Starter

Use this scaffold when creating a new Terraform module. Replace all `REPLACE_*` placeholders with real values before committing.

---

## `versions.tf`

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    # Add additional providers here with pinned versions
  }
}
```

**Replace**: adjust `required_version` to your minimum supported Terraform version. Pin each provider to the major/minor version you tested against.

---

## `variables.tf`

```hcl
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
  description = "Additional tags to merge with the module's common tags. Key-value pairs."
  type        = map(string)
  default     = {}
}

# REPLACE: add module-specific variables below
# variable "REPLACE_var_name" {
#   description = "REPLACE: what this variable controls and any constraints."
#   type        = string  # or number, bool, list(string), map(string), object({...})
# }
```

---

## `main.tf`

```hcl
locals {
  common_tags = merge(
    {
      Environment = var.environment
      Project     = var.project
      ManagedBy   = "terraform"
      Owner       = "REPLACE_team_or_individual"
    },
    var.tags,
  )
}

# REPLACE: add resource blocks below
# resource "aws_REPLACE_resource_type" "REPLACE_resource_name" {
#   # ... arguments ...
#
#   tags = merge(local.common_tags, {
#     Name = "REPLACE_resource_name-${var.environment}"
#   })
# }
```

**Replace**: remove the `Owner` placeholder with the actual team or individual name. Add `tags = merge(local.common_tags, {...})` to every taggable resource.

---

## `outputs.tf`

```hcl
# REPLACE: export key resource IDs and ARNs so consuming modules never hardcode values
# output "REPLACE_resource_id" {
#   description = "REPLACE: what this output represents and when to use it."
#   value       = aws_REPLACE_resource_type.REPLACE_resource_name.id
# }
#
# output "REPLACE_resource_arn" {
#   description = "ARN of the REPLACE resource, used for IAM policy references."
#   value       = aws_REPLACE_resource_type.REPLACE_resource_name.arn
# }
```

Every module must export at least the primary resource's ID and ARN.

---

## `backend.tf`

```hcl
terraform {
  backend "s3" {
    bucket         = "REPLACE_tfstate_bucket_name"
    key            = "REPLACE_module_path/terraform.tfstate"
    region         = "REPLACE_aws_region"
    dynamodb_table = "REPLACE_lock_table_name"
    encrypt        = true
  }
}
```

**Replace**:
- `REPLACE_tfstate_bucket_name` — the S3 bucket that holds remote state for this project
- `REPLACE_module_path` — a unique path per environment, e.g. `prod/vpc/terraform.tfstate`
- `REPLACE_aws_region` — the region where the state bucket lives
- `REPLACE_lock_table_name` — the DynamoDB table used for state locking

For non-AWS backends, remove this file and add the appropriate backend block to `versions.tf`.

---

## Checklist before first `terraform plan`

- [ ] All `REPLACE_*` placeholders removed
- [ ] `terraform fmt` run on all files
- [ ] `terraform init` completed successfully
- [ ] `terraform validate` passes
- [ ] `tflint --recursive` passes with zero warnings
