# Terraform Project Boilerplate Guide

## Purpose & Scope

Step-by-step cookbook for scaffolding a complete Terraform project structure from nothing. Reference this during Phase 0 (Skeleton) of any new infrastructure project.

**Related Documents:**
- [Phase Workflow Guide](vibe_phase_workflow.md) — when each part of this structure gets built
- [State Management Guide](vibe_state_management.md) — backend.tf deep dive

## Root Directory Tree

```
.
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── backend.tf
├── terraform.tfvars.example
├── backend.hcl.example
├── .tflint.hcl
├── .checkov.yaml
├── .gitignore
├── README.md
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── versions.tf
│   ├── alb/
│   │   └── (same 4 files)
│   ├── ecs-service/
│   │   └── (same 4 files)
│   └── static-site/
│       └── (same 4 files)
├── scripts/
│   ├── requirements.txt
│   ├── deploy.py
│   └── verify_deployment.py
├── tests/
│   ├── policy/
│   ├── scripts/
│   └── integration/
└── .github/
    └── workflows/
        └── terraform.yml
```

## File-by-File Content Walkthrough

### 1. `backend.tf` — Remote State Config (Partial)

```hcl
terraform {
  backend "s3" {
    # populated via -backend-config=backend.hcl
  }
}
```

### 2. `backend.hcl.example` — Backend Values Per Environment

```hcl
bucket       = "acme-terraform-state"
key          = "aws-ecs-webapp/dev/terraform.tfstate"
region       = "us-east-1"
encrypt      = true
use_lockfile = true
```

Copy to `backend.dev.hcl`, `backend.staging.hcl`, `backend.prod.hcl` per environment (gitignored is optional here — these files contain no secrets, but treat them consistently with `.tfvars` handling).

### 3. `providers.tf` — Provider Pin + Default Tags

```hcl
terraform {
  required_version = ">= 1.9, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = local.common_tags
  }
}
```

### 4. Root `variables.tf`

```hcl
variable "project" {
  type        = string
  description = "Project name"
}

variable "environment" {
  type        = string
  description = "dev | staging | prod"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}
```

### 5. Root `main.tf` — Local Values + Module Composition

```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

module "vpc" {
  source = "./modules/vpc"
  # ...
}
```

### 6. `terraform.tfvars.example`

```hcl
project     = "acme"
environment = "dev"
aws_region  = "us-east-1"
vpc_cidr    = "10.0.0.0/16"
```

### 7. First Trivial Module — `modules/vpc/versions.tf`

```hcl
terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

## `.gitignore` Requirements

```gitignore
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
crash.log
terraform_plans/

# .terraform.lock.hcl is COMMITTED, not ignored

*.tfvars
*.tfvars.json
!terraform.tfvars.example

.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
```

## Optional: Makefile Command Shortcuts

If this course uses Make elsewhere, mirror the same shortcut convention here:

```makefile
.PHONY: init fmt validate lint scan plan apply

init:
	terraform init

fmt:
	terraform fmt -recursive

validate: fmt
	terraform validate

lint:
	tflint

scan:
	checkov -d . --external-checks-dir tests/policy

plan: validate lint scan
	terraform plan -out=terraform_plans/$(shell date +%Y%m%d%H%M%S).tfplan

apply:
	@echo "Pass the exact plan file: make apply PLAN=terraform_plans/<file>.tfplan"
	terraform apply $(PLAN)
```

## Scaffolding Order (Matches Phase 0 Session)

1. `providers.tf`, `backend.tf` — establish version pins and remote state shape first
2. `variables.tf`, `outputs.tf` at root — the contract
3. `modules/<name>/{main,variables,outputs,versions}.tf` for every planned module, gated behind `var.enabled = false` or `count = 0`
4. `terraform.tfvars.example`
5. `.gitignore`, `.tflint.hcl`, `.checkov.yaml`
6. Root `README.md` documenting `terraform init && terraform plan`
7. `scripts/requirements.txt` + empty script stubs
8. `tests/` directory structure (empty `policy/`, `scripts/`, `integration/`)

Verify with:
```bash
terraform fmt -check -recursive
terraform validate
tflint
terraform plan
```
