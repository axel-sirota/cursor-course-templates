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
- **No application persistence**: Terraform manages infrastructure state via `terraform.tfstate` (remote backend in S3/GCS) — there is no application database. Do not scaffold a database layer.

## Active Phase
- Current: Phase 0 (Planning/Linting)

## Architecture Shape
IaC Playbook — Terraform modules provisioning cloud infrastructure. Not an application. No HTTP server.

## Environment Strategy
Directory-per-environment: `envs/dev/`, `envs/staging/`, `envs/prod/` each call root modules.
Workspaces: only for simple cases with identical topology across envs.
Terragrunt: acceptable for DRY multi-env configs; not required.

## Scope
This stack covers: Terraform/OpenTofu IaC only.
Ansible (config management): see `devops-ansible` stack.
Kubernetes/Helm (app deployment): see `devops-k8s-helm` stack.
Pulumi: out of scope for this stack.

