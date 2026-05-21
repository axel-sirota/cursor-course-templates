# Development Lifecycle Vibe: Terraform IaC

## The IaC session loop

Every working session on Terraform code follows the same rhythm:

1. **Plan the session goal** — write down what resources you intend to add, modify, or remove before writing a line of HCL. Vague goals produce vague plans.
2. **Write or modify resources** — implement the changes in `main.tf`, `variables.tf`, and `outputs.tf`.
3. **Format and validate** — run `terraform fmt`, then `terraform validate`. Fix all issues before moving on.
4. **Lint** — run `tflint --recursive`. Zero new warnings. If a rule fires, fix it or add a suppression with a written justification.
5. **Plan** — run `terraform plan -out terraform_plans/{datetime}.tfplan`. Read the plan output carefully. Every `+`, `~`, and `-` should be expected.
6. **Review the plan** — if anything in the plan is unexpected, stop and investigate before applying.
7. **End the session** — commit the changes, push the branch, and attach the plan output to the PR. Do not apply from a feature branch.

## Branch strategy

Every infrastructure change happens on a feature branch. `main` represents what is currently applied to production — it is not a development branch. Commit directly to `main` only in a genuine emergency, and document why immediately after.

Branch names should describe the change: `feat/add-vpc-flow-logs`, `fix/rds-storage-autoscaling`, `chore/update-aws-provider-5.50`. Ambiguous branch names like `infra-changes` or `axel-work` make the PR review harder.

## PR discipline

Every PR must include the `terraform plan` output as a comment or attached artifact. Reviewers read the plan, not just the diff. A diff shows what changed in code; the plan shows what will change in infrastructure. These are not the same thing.

Plan output must show no unintended resource destroys. If a destroy appears, it must be explicitly called out in the PR description with a justification for why it is intentional and safe.

## Apply discipline

Applies happen from CI after the PR is merged to `main`. This is the rule, not a suggestion. Manual applies from a local machine are emergency procedures only — they bypass review, bypass CI checks, and create state divergence if the local workspace is not up to date.

When a manual apply is unavoidable (CI is broken, time-sensitive incident), log it: record who applied, from what state, and what the plan output showed. Open a follow-up ticket to reconcile the deviation from normal process.

## Drift cadence

Run `terraform plan` against production on a weekly schedule without applying. Any difference between Terraform state and actual infrastructure is drift and must be investigated. Drift accumulates — a small drift ignored this week becomes a larger one next month. Treat drift as a regression: find the root cause, fix it, and prevent recurrence.

Common drift causes: manual changes made during incidents that were never codified, resources modified by other tools, resources modified by AWS automation (e.g., Auto Scaling groups). Each case has a different fix; all cases require investigation before `terraform apply`.
