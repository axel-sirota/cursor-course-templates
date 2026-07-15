# State Management Vibe Coding Guide

## Purpose & Scope

This guide is the deep dive on Terraform's persistence layer — remote state, locking, and cross-module references — the Terraform analog of the reference stack's database guide. Reference this document when configuring a backend, wiring cross-module data, or recovering from state issues.

**Related Documents:**
- [Terraform Boilerplate Guide](vibe_terraform_boilerplate.md) — where `backend.tf` fits in the project tree
- [IAM & Security Guide](vibe_iam_security.md) — least-privilege access to the state bucket itself

**When to use this guide:**
- Setting up a new project's remote backend
- Deciding between S3-native locking and the classic DynamoDB pattern
- Referencing one module's outputs from another module or project
- Recovering from a stuck lock or investigating state drift

## S3 Backend + Locking Setup

### Option A (Recommended for New Projects): Native S3 Locking

Terraform 1.10 introduced `use_lockfile` as an experimental S3-backend option; it became generally available in Terraform 1.11, using S3 conditional writes (`If-None-Match`) to create a `.tflock` object alongside the state file. DynamoDB-based locking is deprecated as of 1.11 and scheduled for removal in a future minor version.

```hcl
terraform {
  backend "s3" {
    bucket       = "acme-terraform-state"
    key          = "aws-ecs-webapp/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

Advantages: no DynamoDB table to provision or pay for, fewer moving parts, and slightly faster lock acquisition since it's a single S3 call instead of coordinating two services.

### Option B (Classic, Still Fully Supported): S3 + DynamoDB

```hcl
terraform {
  backend "s3" {
    bucket         = "acme-terraform-state"
    key            = "aws-ecs-webapp/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "acme-terraform-locks"
  }
}
```

Use this if the team's Terraform version predates 1.10, or if existing tooling/runbooks are already built around the DynamoDB table. Both patterns can be configured simultaneously during a migration — remove `dynamodb_table` and add `use_lockfile = true`, then run `terraform init -reconfigure`.

### This Stack's Default
Default to **native S3 locking** for any project started today. Teach the DynamoDB pattern as the "classic/portable" alternative, since a large share of existing production Terraform still uses it and students will encounter it in the wild.

## `terraform_remote_state` for Cross-Module References

When modules are applied as genuinely separate Terraform projects (different lifecycles, different teams), reference another module's outputs via its state file instead of hardcoding IDs:

```hcl
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "acme-terraform-state"
    key    = "aws-ecs-webapp/vpc/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_ecs_service" "web" {
  network_configuration {
    subnets = data.terraform_remote_state.vpc.outputs.private_subnet_ids
  }
}
```

If modules are composed within a single root project (as in `examples/aws-ecs-webapp`), prefer direct module output references (`module.vpc.outputs.vpc_id`) over `terraform_remote_state` — it's simpler and doesn't require a separate `apply` per module. Reserve `terraform_remote_state` for genuinely independent projects/lifecycles.

## Environment Strategy: Directory-Per-Env, Not Terraform Workspaces

This stack explicitly **rejects Terraform's built-in `workspace` command** for environment separation, in favor of a directory-per-environment (or `tfvars`-per-environment with a distinct backend key per environment) pattern:

```
environments/
├── dev/
│   ├── backend.hcl
│   └── terraform.tfvars
├── staging/
│   ├── backend.hcl
│   └── terraform.tfvars
└── prod/
    ├── backend.hcl
    └── terraform.tfvars
```

```bash
terraform init -backend-config=environments/dev/backend.hcl
terraform plan -var-file=environments/dev/terraform.tfvars -out=terraform_plans/dev-$(date +%Y%m%d%H%M%S).tfplan
```

**Why not workspaces**: `terraform workspace` makes environment separation implicit (which workspace is "selected" right now?) and shares the same `.tf` files across environments with no natural place for environment-specific resource differences (e.g. prod-only `prevent_destroy`, dev-only smaller instance sizes) without littering the code with `terraform.workspace == "prod"` conditionals. Separate `tfvars` + separate backend `key` per environment makes the blast radius of any `plan`/`apply` explicit in the command itself.

## State File Safety Rules

1. **Never edit `.tfstate` by hand.** Not even to "just fix one field." State is a serialized dependency graph, not a config file.
2. **Never delete a `.tfstate` file** — even a broken one. Pull a backup first (`terraform state pull > backup.tfstate`), then work the problem.
3. **`terraform state mv`** — rename a resource address without destroying/recreating (e.g. after refactoring a module):
   ```bash
   terraform state mv aws_instance.web module.ecs_service.aws_instance.web
   ```
4. **`terraform state rm`** — remove a resource from state WITHOUT destroying the real infrastructure (use when adopting existing infra into a different module, or deliberately orphaning a resource):
   ```bash
   terraform state rm aws_s3_bucket.legacy
   ```
5. **`terraform import`** — bring an existing, out-of-band-created resource under Terraform management:
   ```bash
   terraform import aws_s3_bucket.legacy acme-legacy-bucket
   ```
6. **Always `terraform plan` immediately after any state surgery** to confirm the configuration and state now agree.

## Drift Detection

Schedule a read-only `terraform plan` (never `apply`) on a cron/CI schedule to catch manual console changes before they cause a surprising diff during the next real session:

```yaml
# .github/workflows/drift-check.yml (scheduled, plan-only, no apply)
on:
  schedule:
    - cron: "0 13 * * 1-5"  # weekdays, 9am ET
jobs:
  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform plan -detailed-exitcode || echo "::warning::Drift detected"
```

## Anti-Patterns to Avoid

- Running `terraform apply` from two machines/CI runs concurrently without locking enabled
- Using `-target` as a routine substitute for fixing the actual dependency graph
- Sharing one state file across dev/staging/prod (always separate backend `key`s)
- Treating a stuck lock by deleting the lock file/table entry without first confirming no other `apply` is actually in progress
- Committing a populated `.tfvars` with real values instead of `.tfvars.example`
