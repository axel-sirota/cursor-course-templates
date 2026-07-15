# Deploy Lifecycle Vibe Coding Guide

## Purpose & Scope

Git/CI workflow for infrastructure changes — the Terraform analog of the reference stack's development-lifecycle guide. Reference this when setting up branch protection, PR workflows, or promotion strategy across environments.

**Related Documents:**
- [Phase Workflow Guide](vibe_phase_workflow.md) — session-level workflow within a single environment
- [State Management Guide](vibe_state_management.md) — directory-per-environment strategy this lifecycle assumes

## The Core Flow

```
feature branch
      │
      ▼
  open PR  ──────►  CI: fmt-check → validate → tflint → checkov → plan
      │                                                      │
      │                                              plan posted as PR comment
      │                                                      │
      ▼                                                      ▼
  human review  ◄─────────────────────────────────  reviewer reads the plan diff
      │
      ▼
  merge to main
      │
      ▼
  CI: apply (manual-approval gate via GitHub Environments)
      │
      ▼
  post-apply smoke check
```

## Feature Branch → PR → Plan

1. Create a branch per module/change: `git checkout -b add-ecs-autoscaling`
2. Make the HCL change (following `301-module-phase.mdc` session discipline)
3. `terraform fmt -recursive` locally before pushing
4. Open a PR — CI runs `fmt-check → validate → tflint → checkov → plan`
5. The plan output is posted as a PR comment (see `templates/ci-pipeline-template.yml`)
6. Reviewer reads the plan diff — looks specifically for unexpected `destroy`/`replace` actions

## Review → Merge → Apply

- `apply` never runs on a PR branch — only on `main` (or the environment's protected branch), and only after merge
- The `apply` job is gated behind a GitHub Environment's manual-approval rule — a human clicks "Approve" in the Actions UI before `apply` executes
- After `apply`, a post-apply smoke check (boto3/aws-cli) confirms the real resource is healthy before the workflow reports success

## Promotion Strategy Across Environments

This stack uses **directory-per-environment `tfvars` + separate backend keys** (see `vibe_state_management.md`), not a single shared state promoted via workspace switching. Promotion looks like:

```bash
# Same HCL, different tfvars/backend per environment — promote by re-running
# the identical plan/apply against the next environment's config, not by
# copying resources or state.

terraform init -backend-config=environments/dev/backend.hcl
terraform plan -var-file=environments/dev/terraform.tfvars -out=terraform_plans/dev.tfplan
terraform apply terraform_plans/dev.tfplan

# ... validated in dev, PR merged, CI re-runs against staging ...

terraform init -reconfigure -backend-config=environments/staging/backend.hcl
terraform plan -var-file=environments/staging/terraform.tfvars -out=terraform_plans/staging.tfplan
terraform apply terraform_plans/staging.tfplan

# ... then prod, typically with a required manual approval and possibly a
# separate, more restricted IAM role ...
```

CI matrices this per-environment, running the same plan/apply job three times with different `-backend-config`/`-var-file` inputs, with `prod` gated behind its own GitHub Environment approval (often requiring a different, more senior reviewer group than staging).

## Rollback: Reapply the Previous Plan, Never Hand-Edit State

If an `apply` introduces a regression:

1. **Do not** touch `.tfstate` directly.
2. Identify the last-known-good commit: `git log -- modules/<affected-module>/`
3. Revert the HCL: `git revert <bad-commit>` (creates a new commit, preserves history — never `git reset --hard` on a shared branch)
4. Let the normal PR → plan → review → apply flow run again against the reverted HCL
5. If the regression is urgent and blocking, the manual-approval gate can be used to expedite review, but the flow itself is never bypassed by applying un-reviewed HCL directly from a laptop against `prod`

## Hotfix Exception

For a genuine production incident, a hotfix branch follows the identical flow — branch, PR, plan-as-comment, review, merge, gated apply — just with an expedited review SLA. The only thing that changes is review speed, never the presence of `plan` review or the manual-approval gate.

## Anti-Patterns to Avoid

- Applying directly from a developer's laptop against a shared environment's state
- Force-pushing over a branch that already has an open PR with a posted plan comment (invalidates the reviewed plan — CI must re-plan)
- Approving an `apply` without having read the plan diff
- Skipping staging and applying an untested module change straight to prod
- Using `terraform workspace select prod` as a substitute for a distinct backend key and a distinct, reviewed `tfvars` file
