# Project Context: DevOps Ansible

## Tech Stack
- Tool: Ansible 9+ (ansible-core 2.16+)
- Testing: Molecule (Docker driver for unit, Vagrant for systemd-heavy roles)
- Linting: ansible-lint
- Inventory: static YAML or dynamic (AWS EC2 plugin, Terraform outputs)
- Secrets: Ansible Vault or HashiCorp Vault lookup plugin
- CI/CD: GitHub Actions or GitLab CI

## Architecture Shape
IaC Playbook — configuration management and application deployment on existing servers.
Not infrastructure provisioning (use devops-terraform for that).
Ansible configures what Terraform created.

## Vibe & Style
- Coding Style: YAML. snake_case for variable names. Descriptive task names (imperative).
- Architecture: Role-based. One role = one responsibility. Playbooks orchestrate roles.
- Pattern: Inventory → Playbook → Roles → Tasks/Handlers/Templates/Defaults.

## Key Rules
- Every role must have Molecule tests.
- All tasks must be idempotent — running twice produces same result.
- No hardcoded values in tasks — use defaults/main.yml for all configurable values.
- Use handlers for service restarts — never restart in a task directly.
- Secrets in Ansible Vault — never plaintext in vars files.

## Entry Point & Structure
- **Entry point**: `site.yml` — top-level playbook that imports all roles; run with `ansible-playbook site.yml -i inventories/dev/hosts.yml`
- **Role entry**: `roles/{role_name}/tasks/main.yml` — first file executed for a role
- **Config/env**: `group_vars/{group}/vault.yml` (Ansible Vault encrypted) for secrets; `group_vars/{group}/vars.yml` for non-secret group config; `host_vars/{host}/vars.yml` for host-specific overrides
- **No persistence**: Ansible configures servers — there is no application database to scaffold
- **Test command**: `molecule test` (full converge + idempotency + verify cycle)

## Active Phase
- Current: Phase 0 (Skeleton)
