# Session 1 — Fix `devops-terraform` (STUB → COMPLETE)

**Phase:** 1
**Parallel with:** Sessions 2–6
**Depends on:** nothing
**Next:** Session 13 (after all phase 1+2 done)

## Current state
```
stacks/devops-terraform/
├── context.md          ← missing Architecture Shape, AWS-only bias
└── rules/
    └── devops-standards.mdc   ← 1 file, no numeric prefix
```
No `templates/`, no `vibe/`, no `examples/`.

---

## Files to Create / Update

```
stacks/devops-terraform/
├── context.md                          ← UPDATE (add Architecture Shape, multi-cloud note, workspace strategy)
├── rules/
│   ├── 000-tf-workflow.mdc             ← NEW
│   ├── 100-tf-architecture.mdc         ← NEW
│   ├── 200-tf-validate.mdc             ← NEW
│   ├── 300-tf-style.mdc                ← NEW
│   └── devops-standards.mdc            ← RENAME to 400-devops-standards.mdc + minor fixes
├── templates/
│   ├── terraform-starter.md            ← NEW
│   └── phase-checklist.md              ← NEW
├── vibe/
│   ├── vibe_architecture.md            ← NEW
│   └── vibe_development_lifecycle.md   ← NEW (can reference stacks/shared/ once session 6 done)
└── examples/
    └── vpc-module/
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── versions.tf
```

---

## File Specifications

### `context.md` (UPDATE)

Add after existing content:

```markdown
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
```

### `rules/000-tf-workflow.mdc`

Frontmatter: `description: Terraform workflow gates`, `alwaysApply: true`

Rules:
- **Plan before apply**: Always `terraform plan -out terraform_plans/{datetime}.tfplan`. Never `terraform apply` without a saved plan.
- **PR gate**: Attach plan output to every PR. Apply only after merge, never on feature branches.
- **Destroy protection**: Never run `terraform destroy` yourself. Flag any resource needing removal; let the human apply.
- **Drift detection**: Schedule weekly `terraform plan` against production; treat drift as a bug.
- **Init every time**: Run `terraform init` for new modules and after `versions.tf` changes.

### `rules/100-tf-architecture.mdc`

Frontmatter: `description: Terraform module structure and layering`, `alwaysApply: true`

Rules:
- **Module files**: Every module must have `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`. No single-file modules.
- **Module versioning**: Pin all registry modules with `version = "~> X.Y"`. Pin all git modules with `?ref=vX.Y.Z`.
- **Remote state**: Remote state with locking is mandatory. AWS: S3 + DynamoDB. Azure: Storage Account + blob lock. GCP: GCS. Terraform Cloud: native.
- **No hardcoded values**: All environment-specific values in `variables.tf` with descriptions. No magic strings in `main.tf`.
- **Outputs**: Every module exports its key resource IDs and ARNs via `outputs.tf`. Consuming modules reference outputs, never hardcode IDs.
- **Least privilege**: IAM roles/policies created by Terraform must follow least-privilege. No `*` actions without explicit justification comment.

### `rules/200-tf-validate.mdc`

Frontmatter: `description: Terraform validation and security scanning`, `alwaysApply: true`

Rules:
- **CI gate order**: `terraform fmt -check` → `terraform validate` → `tflint` → `checkov` → `terraform plan -out`. All must pass before PR merge.
- **tflint**: Run with `--recursive`. Zero warnings allowed in new modules.
- **checkov**: Run with `--framework terraform`. HIGH severity findings block merge. MEDIUM findings require inline suppression with justification.
- **`prevent_destroy`**: Set `lifecycle { prevent_destroy = true }` on any resource that holds state (databases, S3 buckets with versioning, KMS keys).
- **Secrets**: No secrets in `.tf` files or `terraform.tfvars`. Use `TF_VAR_*` env vars or a secrets manager reference. `sensitive = true` on all secret variables.

### `rules/300-tf-style.mdc`

Frontmatter: `description: HCL naming and formatting conventions`, `alwaysApply: true`

Rules:
- **Formatting**: `terraform fmt` before every commit. CI enforces `terraform fmt -check`.
- **Naming**: `snake_case` for all resource names, variable names, output names. No hyphens in Terraform identifiers.
- **Resource naming**: `{purpose}_{type}` — e.g., `web_security_group`, `app_db_instance`.
- **Tagging**: Every cloud resource must have at minimum: `Environment`, `Project`, `ManagedBy = "terraform"`, `Owner` tags. Define a `local.common_tags` map and merge into each resource.
- **Comments**: Use `#` comments to explain WHY a resource exists or WHY a non-obvious setting was chosen. Do not comment what the resource type already conveys.
- **Variable descriptions**: Every variable must have a `description`. Type constraints required on all variables.

### `templates/terraform-starter.md`

Scaffold showing the canonical module layout with:
- `versions.tf` with `required_version` and `required_providers` block (pinned)
- `variables.tf` with example variable + description + type
- `outputs.tf` with example output
- `main.tf` with example resource + `local.common_tags` merge
- `backend.tf` showing S3 + DynamoDB remote state block
- Inline instructions for what to replace

### `templates/phase-checklist.md`

Phase gates for IaC work:

**Phase 0 — Planning:**
- [ ] Module directory structure created with all 4 required files
- [ ] Variables defined with descriptions and types
- [ ] Remote state backend configured
- [ ] `terraform init` succeeds

**Phase 1 — Scaffold:**
- [ ] All resources stubbed (empty or minimal `resource` blocks)
- [ ] `terraform validate` passes
- [ ] `tflint` passes (zero warnings)
- [ ] Plan output reviewed and attached

**Phase 2 — Implementation:**
- [ ] All resource arguments filled in (no `TODO` values)
- [ ] `checkov` passes (no HIGH findings)
- [ ] `terraform plan` output reviewed — no unintended destroys
- [ ] All sensitive values use `sensitive = true`

**Phase 3 — Handoff:**
- [ ] `terraform-docs` or equivalent README generated
- [ ] `prevent_destroy` set on stateful resources
- [ ] Plan output attached to PR
- [ ] Applied to staging; verified in prod-equivalent env

### `vibe/vibe_architecture.md`

Sections:
- **What Terraform is for**: provisioning infrastructure, not configuring it. Cattle not pets. Immutable when possible.
- **Module design philosophy**: small, focused, composable. A module that does 5 things should be 5 modules.
- **When to use workspaces vs directories**: workspaces for identical topology; directories for genuinely different environments.
- **When to reach for Terragrunt**: only when you have 4+ environments with identical structure and DRY is genuinely painful without it.
- **Terraform vs Ansible**: Terraform creates resources. Ansible configures what's running on them. Never configure OS-level settings in Terraform.
- **Terraform vs Kubernetes/Helm**: Terraform creates the cluster. Helm deploys apps into it. Don't manage K8s workloads with Terraform kubernetes_manifest resources in production.
- **The state file is sacred**: Never delete it. Never edit it manually. If it drifts, investigate before touching.

### `vibe/vibe_development_lifecycle.md`

Sections:
- **The IaC session loop**: plan session goal → write/modify resources → `fmt` + `validate` + `tflint` → plan → review → end session
- **Branch strategy**: feature branches for all changes. `main` = what's applied to prod. Never commit directly to main.
- **PR discipline**: every PR has a plan output. Reviewer reads the plan, not the diff.
- **Apply discipline**: applies happen from CI after merge. Manual applies are emergencies only and must be logged.
- **Drift cadence**: weekly plan against prod; drift is treated as a regression.

### `examples/vpc-module/`

Four files showing a real, minimal, working VPC module:
- `versions.tf`: required_version ≥ 1.6, aws provider ~> 5.0
- `variables.tf`: `vpc_cidr`, `environment`, `project`, `tags` (with descriptions + types)
- `main.tf`: `aws_vpc` resource with `local.common_tags`, `aws_internet_gateway`, `aws_subnet` (one public)
- `outputs.tf`: `vpc_id`, `subnet_id`, `internet_gateway_id`

---

## Acceptance Criteria

- [ ] `ls stacks/devops-terraform/rules/` shows 5 files (000, 100, 200, 300, 400)
- [ ] `ls stacks/devops-terraform/templates/` shows `terraform-starter.md` and `phase-checklist.md`
- [ ] `ls stacks/devops-terraform/vibe/` shows 2 docs
- [ ] `ls stacks/devops-terraform/examples/vpc-module/` shows 4 `.tf` files
- [ ] `context.md` contains `## Architecture Shape` section
- [ ] `rules/000-tf-workflow.mdc` contains "plan -out" enforcement rule
- [ ] No mention of HTTP, REST, API, endpoints anywhere in any new file
