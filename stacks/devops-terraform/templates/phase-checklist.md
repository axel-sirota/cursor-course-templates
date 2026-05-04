# IaC Phase Checklist

Use this checklist to gate progress through each phase of a Terraform module or infrastructure change. Do not advance to the next phase until all items in the current phase are checked.

---

## Phase 0 — Planning

- [ ] Module directory structure created with all 4 required files: `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`
- [ ] Variables defined in `variables.tf` with descriptions and type constraints for all inputs
- [ ] Remote state backend configured in `backend.tf` (S3 + DynamoDB, or equivalent for cloud provider)
- [ ] `terraform init` succeeds with no errors or version conflict warnings
- [ ] Module purpose and scope documented (in a README or comment block in `main.tf`)

---

## Phase 1 — Scaffold

- [ ] All resources stubbed — minimal or empty `resource` blocks that establish structure
- [ ] `terraform validate` passes — no syntax errors or internal consistency issues
- [ ] `tflint --recursive` passes — zero warnings in the module
- [ ] `terraform plan -out terraform_plans/{datetime}.tfplan` output reviewed and attached to the PR or task
- [ ] No `TODO` comments left in resource arguments (stubs are OK; incomplete arguments are not)

---

## Phase 2 — Implementation

- [ ] All resource arguments filled in — no placeholder values remaining
- [ ] `checkov --framework terraform` passes — no HIGH severity findings
- [ ] MEDIUM checkov findings either resolved or suppressed with inline `checkov:skip` and written justification
- [ ] `terraform plan` output reviewed — no unintended resource destroys in the plan
- [ ] All sensitive variable values use `sensitive = true`
- [ ] `local.common_tags` defined and merged into every taggable resource
- [ ] IAM policies reviewed for least-privilege — no `"*"` actions without justification comment

---

## Phase 3 — Handoff

- [ ] `terraform-docs` or equivalent README generated with input/output documentation
- [ ] `lifecycle { prevent_destroy = true }` set on all stateful resources (databases, versioned S3 buckets, KMS keys)
- [ ] Plan output attached to the pull request for reviewer inspection
- [ ] Applied to staging environment and verified — resource state matches expected outputs
- [ ] Applied to prod-equivalent environment or sign-off from team lead that staging verification is sufficient
- [ ] Post-apply `terraform plan` run against staging confirms zero drift
