---
description: Run Terraform infrastructure workflow (Init -> Plan -> Apply)
---

# Terraform Workflow Command

Safely manage infrastructure changes. This command enforces the "Plan First" discipline.

## Prerequisites
- Terraform installed.
- Directory `terraform/` or `infra/` exists.

## The Workflow

**1. Init (if needed)**
- Check if `.terraform` exists. If not, run `terraform init`.

**2. Plan (Mandatory)**
- Run `terraform plan -out=tfplan`.
- **Review**: Summarize the changes (Additions, Changes, Destructions).
- **Safety**: If "Destroy" count is high, warn the user explicitly.

**3. Apply**
- Ask for confirmation: "Apply these changes?"
- Run `terraform apply tfplan`.

## State Management
- Verify remote state configuration before planning.
- Ensure state locking is active.

## Usage
`@terraform "Add S3 bucket"` -> *Generates HCL, runs Plan, asks to Apply.*

