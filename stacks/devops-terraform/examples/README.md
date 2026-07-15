# Reference Solution: AWS ECS Web App

**TEACHER ONLY** — Complete working example for reference

## What This Is

A complete Terraform project implementing the session-based IaC workflow: a VPC, an ECS Fargate service behind an Application Load Balancer, and an S3 + CloudFront static frontend, with remote state on S3 (native locking). Use this to:
- Understand the complete module structure
- Reference during demos
- Debug student issues
- Prepare for sessions

## Features Implemented
- VPC with public/private subnets across 2 AZs, single NAT gateway (dev-sized)
- ALB with HTTP→HTTPS redirect and a health-checked target group
- ECS Fargate service running behind the ALB
- S3 + CloudFront static frontend
- Python/boto3 `verify_deployment.py` CLI for post-apply health checks
- checkov custom policy check + tflint config
- pytest + moto/Stubber unit tests for the automation script
- GitHub Actions CI/CD pipeline (fmt/validate/lint/scan/plan-as-PR-comment/apply-with-approval)

## Quick Start

```bash
cd examples/aws-ecs-webapp

# One-time, by hand, before first init (see rules/000-environment-setup.mdc):
#   create the S3 state bucket

cp backend.hcl.example backend.hcl   # fill in your bucket name
cp terraform.tfvars.example terraform.tfvars   # fill in your values

terraform init -backend-config=backend.hcl
terraform plan -out=terraform_plans/initial.tfplan
terraform apply terraform_plans/initial.tfplan
```

Visit the ALB DNS name from `terraform output alb_dns_name`.

## Structure

Follows `vibe_terraform_boilerplate.md` exactly:
- `main.tf` / `variables.tf` / `outputs.tf` / `providers.tf` / `backend.tf` — root orchestration
- `modules/` — `vpc`, `alb`, `ecs-service`, `static-site`
- `scripts/` — Python/boto3 `verify_deployment.py`
- `tests/` — checkov policy checks, pytest+moto/Stubber unit tests, tests/README.md

## Phases Implemented
- Phase 0: Skeleton (all modules scaffolded, `terraform plan` only)
- Phase 1: `modules/vpc` (networking foundation)
- Phase 2: `modules/alb` + `modules/ecs-service` (compute + routing)
- Phase 3: `modules/static-site` (S3 + CloudFront)
- Phase 4: CI/CD wiring (`.github/workflows/terraform.yml`)

## Testing

```bash
terraform fmt -check -recursive
terraform validate
tflint
checkov -d . --external-checks-dir tests/policy

.venv/bin/python3 -m pytest tests/ -v -m "not e2e"
```

All static, policy, and script-unit checks pass without needing real AWS credentials. The `e2e`-marked tests apply real infrastructure into a throwaway workspace and cost money — run manually.
