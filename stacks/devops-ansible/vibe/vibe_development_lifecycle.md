# Ansible Development Lifecycle Vibe

## Shared Lifecycle Foundation

This stack follows the shared development lifecycle at `stacks/shared/` for general practices:
- Git branching and PR workflow
- Code review gates
- Commit message conventions
- CI/CD pipeline structure

The sections below add Ansible-specific practices on top of that foundation.

## Molecule-First Development Loop

Write the test before writing the task. This is not theoretical — it changes how you think about the role.

1. **Define the end state** — what should be true after the role runs? (nginx is running, port 80 is open, config file exists at `/etc/nginx/nginx.conf`)
2. **Write `verify.yml` assertions** for each of those conditions (they will fail because nothing is implemented yet)
3. **Run `molecule create`** to spin up the test container
4. **Implement tasks** in `install.yml` and `configure.yml`
5. **Run `molecule converge`** — iterate until all tasks succeed
6. **Run `molecule idempotence`** — iterate until `changed=0` on second run
7. **Run `molecule verify`** — iterate until all assertions pass
8. **Run `molecule test`** — full lifecycle must pass clean before PR

Keep the container running during development. `molecule destroy` only when done or switching context.

## ansible-lint in Pre-Commit Hooks

Install `ansible-lint` as a pre-commit hook so style violations are caught before commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/ansible/ansible-lint
    rev: v24.2.0
    hooks:
      - id: ansible-lint
```

Run before every commit:
```bash
pre-commit run ansible-lint --all-files
```

ansible-lint enforces:
- FQCN on all module calls
- Imperative task names
- No `warn` or deprecated syntax
- YAML formatting (via yamlint integration)

Fix all lint violations before committing. Never use `# noqa` unless you have a documented reason and team sign-off.

## Vault Rotation Discipline

Ansible Vault secrets must be rotated on a regular schedule (at minimum annually, or immediately after any personnel change or suspected exposure).

Rotation process:
1. Generate new secret value (password manager, `openssl rand -base64 32`, etc.)
2. Re-encrypt with new value: `ansible-vault encrypt_string '{new_secret}' --name '{var_name}'`
3. Update the affected `vars/` file with the new encrypted string
4. Run full `molecule test` to verify the role still works with new secret
5. Deploy to staging → validate → deploy to production
6. Revoke old secret at the source (database user, API token, etc.)
7. Update vault password in CI secret store and password manager

Never:
- Rotate in production without first testing in staging
- Leave old secrets active after rotation completes
- Store vault passwords in the repository

## Role Development Checklist (Quick Reference)

```
[ ] ansible-galaxy role init roles/{name}
[ ] molecule/default/ created with molecule.yml + converge.yml + verify.yml
[ ] verify.yml assertions written (test-first)
[ ] defaults/main.yml variables defined with {rolename}_ prefix
[ ] tasks/install.yml + tasks/configure.yml implemented
[ ] handlers/main.yml restart handler defined
[ ] molecule test → all phases green
[ ] ansible-lint → zero warnings
[ ] PR created → CI gates pass → review → merge
```

## Feature Branch Workflow

```bash
git checkout -b feat/add-nginx-role
# develop role
molecule test
ansible-lint roles/nginx/
git add roles/nginx/ molecule/
git commit -m "feat(nginx): add nginx install and configure role with Molecule tests"
git push origin feat/add-nginx-role
# open PR → CI runs ansible-lint + molecule test → review → merge
```

One role = one PR. Do not batch multiple unrelated role changes in a single PR.
