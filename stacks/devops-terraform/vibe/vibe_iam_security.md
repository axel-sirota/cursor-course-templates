# IAM & Security Vibe Coding Guide

## Purpose & Scope

This stack needs a security-specific guide the reference stack doesn't, since least-privilege IAM is as central to Terraform/AWS work as authentication is to a web API. Reference this guide when writing any `aws_iam_role`, `aws_iam_policy`, or CI credential configuration.

**Related Documents:**
- [Deploy CI/CD Rule](../rules/501-deploy-cicd.mdc) — the OIDC workflow this guide's CI section assumes
- [Environment Setup Rule](../rules/000-environment-setup.mdc) — local AWS credential setup

**When to use this guide:**
- Writing any IAM role or policy
- Wiring GitHub Actions (or GitLab CI) to AWS
- Deciding where a secret lives (tfvars vs. SSM vs. Secrets Manager)
- Triaging a checkov/tfsec IAM finding

## Least-Privilege IAM Role/Policy Patterns

### Use `aws_iam_policy_document` Data Source, Not Inline JSON Strings

```hcl
data "aws_iam_policy_document" "ecs_task_s3_read" {
  statement {
    sid       = "ReadUploadsBucket"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.uploads.arn}/*"]
  }
}

resource "aws_iam_role_policy" "ecs_task_s3_read" {
  name   = "${local.name_prefix}-ecs-task-s3-read"
  role   = aws_iam_role.task.id
  policy = data.aws_iam_policy_document.ecs_task_s3_read.json
}
```

Prefer this over `jsonencode({...})` or raw heredoc JSON — the data source validates policy syntax at `terraform validate` time and gets IDE/HCL tooling support that a plain string doesn't.

### Scope Resources, Never `Resource = "*"` Without Justification

```hcl
# Bad
statement {
  actions   = ["s3:*"]
  resources = ["*"]
}

# Good — scoped to exactly what the task needs
statement {
  actions   = ["s3:GetObject", "s3:PutObject"]
  resources = ["${aws_s3_bucket.uploads.arn}/*"]
}
```

If a wildcard is genuinely unavoidable (some AWS actions have no resource-level permission support, e.g. certain `ec2:Describe*` calls), document why in a comment next to the statement.

### Separate Execution Role From Task Role (ECS-Specific)

- **Execution role**: what ECS itself needs to start the task — pull the image, write logs, read secrets referenced in the task definition. Attach `AmazonECSTaskExecutionRolePolicy` plus a scoped `secretsmanager:GetSecretValue`/`ssm:GetParameters` statement.
- **Task role**: what the *application code* is allowed to call at runtime (S3, DynamoDB, SQS, etc.). Never grant application permissions on the execution role — a compromised container shouldn't automatically inherit "can pull any image" style permissions, and a compromised execution path shouldn't inherit application data access.

## OIDC Federation for CI — No Static Keys

See `rules/501-deploy-cicd.mdc` Part A for the full `aws_iam_openid_connect_provider` + trust policy HCL. The key security properties:

- The trust policy's `StringLike` condition on `token.actions.githubusercontent.com:sub` restricts which repo AND branch/ref can assume the role — scope it to `repo:acme/infra:ref:refs/heads/main` for the `apply` role, not a bare `repo:acme/infra:*`.
- Use **two roles**, not one: a read-only/plan role assumable from any branch (for the PR `plan` job) and a narrower apply role assumable only from `main` (for the `apply` job). Never let a PR-triggered job assume the apply-capable role.
- No `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` ever stored as a GitHub Actions secret for this pipeline — OIDC-assumed temporary credentials only.

## checkov / tfsec Finding Triage Workflow

1. Run `checkov -d .` (or `tfsec .`) and read every finding — do not blanket-suppress a category.
2. For each finding, classify:
   - **Fix it**: the overwhelming majority — add the missing `sensitive = true`, encryption block, or scoped policy.
   - **Skip with justification**: a genuine, reviewed exception (e.g. an intentionally public dev-only subnet). Use `.checkov.yaml`'s `skip-check` with a comment, or an inline `# checkov:skip=CKV_ID:reason` — never a bare skip with no reason.
   - **Escalate**: a finding that reveals a design problem too large to fix inline (e.g. "this whole module needs a redesign for least privilege") — stop and raise it rather than silently skipping.
3. Re-run the scan after fixing; confirm the finding count only decreases, never track "acceptable" counts that creep up over time.

## Secrets Handling: SSM Parameter Store / Secrets Manager, Not `.tfvars`

```hcl
resource "aws_ssm_parameter" "db_password" {
  name  = "/${var.project}/${var.environment}/db_password"
  type  = "SecureString"
  value = var.db_password # var.db_password itself comes from TF_VAR_db_password at apply time, never committed

  lifecycle {
    ignore_changes = [value] # rotated out-of-band; Terraform shouldn't fight a rotation
  }
}
```

Reference it from the ECS task definition's `secrets` block (see `templates/ecs-service-main.md`) rather than injecting the raw value as a plaintext container `environment` variable. The execution role (not the task role) needs `ssm:GetParameters`/`secretsmanager:GetSecretValue` scoped to exactly this parameter's ARN.

## Anti-Patterns to Avoid

- `Resource = "*"` on any IAM statement without an inline justification comment
- One shared IAM role for both CI plan and CI apply, assumable from any branch
- Long-lived AWS access keys stored as GitHub Actions secrets
- Plaintext secrets in `environment` blocks instead of `secrets` blocks backed by SSM/Secrets Manager
- Blanket `skip-check` entries in `.checkov.yaml` with no reason comment
- Granting the execution role application-level data permissions (S3, DynamoDB) that belong on the task role
