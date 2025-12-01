# Project Context: DevOps & Infrastructure

## Tech Stack
- **IaC**: Terraform (OpenTofu compatible)
- **Scripting**: Python 3 (Boto3, Click), Bash
- **Containers**: Docker, Docker Compose
- **Testing**: TFLint, Checkov, Pytest (for scripts)
- **CI/CD**: GitHub Actions / GitLab CI

## Vibe & Style
- **Terraform Style**: Snake_case resource names. Variables in `variables.tf`, outputs in `outputs.tf`.
- **Architecture**: Modular Infrastructure.
  - `main.tf` (Root orchestration)
  - `modules/` (Reusable components)
  - `scripts/` (Glue code)

## Key Rules
- **State**: Remote state with locking (S3 + DynamoDB) is mandatory for team projects.
- **Pinning**: Always pin provider and module versions.
- **Idempotency**: All scripts must be idempotent (safe to run multiple times).
- **Validation**: Run `terraform validate` and `tflint` before commit.
- **Secrets**: No secrets in code. Use `var.TF_VAR_name` or Vault.

## Active Phase
- Current: Phase 0 (Planning/Linting)

