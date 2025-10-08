# Terraform Infrastructure Command

Manage infrastructure using Terraform with proper planning and state management.

## Prerequisites

Before running Terraform commands, read:
- @vibe/vibe_development_lifecycle.md - Deployment patterns
- @templates/docker-compose-template.yaml - Infrastructure reference
- Any existing terraform/ configuration files

## Terraform Workflow

### 1. Initialization
```bash
terraform init
```
Run `terraform init` every time for new modules or when working directory changes.

### 2. Planning
```bash
# Create timestamped plan file
PLAN_FILE="terraform_plans/$(date +%Y%m%d_%H%M%S).tfplan"
terraform plan -out="$PLAN_FILE"
```

**Requirements:**
- Always use `-out` parameter with timestamped plan file
- Plan files stored in `terraform_plans/` directory (gitignored)
- Format: `terraform_plans/YYYYMMDD_HHMMSS.tfplan`

### 3. Application
```bash
# Apply specific plan
terraform apply "$PLAN_FILE"
```

**Requirements:**
- Always apply from a specific plan file
- Never run `terraform apply` without `-out` plan
- Verify plan contents before applying

## Directory Structure

```
terraform/
├── main.tf                 # Main configuration
├── variables.tf           # Variable definitions
├── outputs.tf            # Output definitions
├── terraform_plans/      # Plan files (gitignored)
│   └── 20240101_120000.tfplan
└── .terraform/           # Terraform state (gitignored)
```

## Safety Rules

### ✅ DO
- Always run `terraform init` first
- Use timestamped plan files
- Apply only from specific plans
- Review plan output before applying
- Keep terraform_plans/ in .gitignore

### ❌ NEVER
- Run `terraform destroy` without explicit user request
- Delete .tfstate or .tfstate.* files
- Run `terraform apply` without plan file
- Commit plan files to git
- Run terraform commands without initialization

## Integration with Development

When using with development workflow:
1. Update infrastructure as needed for current session
2. Plan changes with timestamped file
3. Review plan for session requirements
4. Apply only if plan is correct
5. Document infrastructure changes in session summary

## Session Integration

For session-based development:
- Infrastructure changes should align with current session objectives
- Document infrastructure modifications in @plan/sessions/session-N-summary.md
- Ensure infrastructure supports current phase requirements
