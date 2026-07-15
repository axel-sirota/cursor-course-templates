# Project Context: DevOps & Infrastructure

## Tech Stack
- **IaC**: Terraform >= 1.9 (OpenTofu >= 1.7 compatible). Prefer native S3 state locking (`use_lockfile = true`, GA since Terraform 1.11) for new projects; DynamoDB-table locking is still taught as the classic/portable pattern.
- **Cloud**: AWS (provider `hashicorp/aws ~> 5.0`)
- **Scripting**: Python 3.11+ (Boto3, Click), Bash
- **Containers**: Docker, Docker Compose (for the ops-tooling image, not for Terraform itself)
- **Tooling**: `tflint`, `checkov`, `terraform-docs`, `terraform fmt`
- **Testing**: TFLint, Checkov, Pytest + moto (for scripts), optional Terratest/pytest+boto3 for live-apply integration checks
- **CI/CD**: GitHub Actions (primary), GitLab CI patterns noted where they diverge

## Vibe & Style
- **Terraform Style**: snake_case for resources/variables/outputs. Every module follows the same file layout:
  - Root: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, `backend.tf`, `terraform.tfvars.example`
  - `modules/<name>/`: `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`
  - `scripts/`: Python automation (boto3/click)
  - `tests/`: checkov policy tests, tflint config, pytest+moto unit tests, optional integration tests
- **Naming convention**: AWS resources are named `<project>-<env>-<resource>`, e.g. `acme-prod-ecs-cluster`, tagged via a shared `local.common_tags` map.
- **Architecture**: Modular Infrastructure — root module orchestrates reusable `modules/`; no business logic duplicated across modules.

## Key Rules
- **State**: Remote state with locking (S3 native lock file or S3 + DynamoDB) is mandatory for team projects. Never edit `.tfstate` by hand.
- **Plan before Apply**: Never `terraform apply` without a saved plan file (`terraform plan -out=terraform_plans/<timestamp>.tfplan`, then `terraform apply terraform_plans/<timestamp>.tfplan`). This mirrors the repo-wide `terraform_plans/` convention.
- **Pinning**: Always pin provider (`~> 5.0`) and module (`~> X.Y`, or `?ref=vX.Y.Z` for git sources) versions. Never float on `latest` or an unpinned major.
- **Idempotency**: All scripts must be idempotent (safe to run multiple times).
- **Validation**: Run `terraform fmt -check -recursive`, `terraform validate`, and `tflint` before every commit; `checkov -d .` before every plan review.
- **Secrets**: No secrets in code. Use `TF_VAR_*` env vars, SSM Parameter Store/Secrets Manager, or Vault. `.tfvars` files are gitignored; only `terraform.tfvars.example` is committed.

## Active Phase
- Current: Phase 0 (Skeleton — plan-only, no `apply`). Phase 1+ sessions apply one module or resource group at a time; see `rules/` for the full session-phase workflow.

