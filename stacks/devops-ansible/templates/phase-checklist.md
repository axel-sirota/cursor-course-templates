# Ansible Role Phase Checklist

## Phase 0 — Skeleton

- [ ] Role structure initialized with `ansible-galaxy role init roles/{rolename}`
- [ ] `molecule/default/` directory created with `molecule.yml` + `converge.yml` + `verify.yml`
- [ ] `molecule create` succeeds (Docker container starts cleanly)
- [ ] `ansible-lint` passes on empty skeleton (no YAML errors, no lint violations)
- [ ] `defaults/main.yml` created with `{rolename}_` prefixed placeholder variables
- [ ] `meta/main.yml` completed with `galaxy_info` (author, description, platforms)
- [ ] `handlers/main.yml` created with `restart {rolename}` handler stub

## Phase 1+ — Implementation

- [ ] `tasks/install.yml` — package install tasks using `ansible.builtin.package`
- [ ] `tasks/configure.yml` — config file tasks using `ansible.builtin.template`
- [ ] `tasks/main.yml` — imports `install.yml` and `configure.yml` via `ansible.builtin.import_tasks`
- [ ] `molecule converge` succeeds (tasks run without error on first run)
- [ ] `molecule idempotence` passes (zero `changed` tasks on second run)
- [ ] All configurable values are in `defaults/main.yml` with `{rolename}_` prefix
- [ ] No hardcoded values exist in task files — all values reference variables
- [ ] Service restarts via `notify:` handler only — no `state: restarted` in tasks
- [ ] No secrets committed in plaintext — all secrets use `ansible-vault encrypt_string`
- [ ] All tasks use FQCN (`ansible.builtin.*`)
- [ ] All task names are present-tense imperative sentences
- [ ] `become: true` only on tasks that require root — not at play level unless needed

## Handoff (Ready to Merge)

- [ ] `molecule verify` passes — service running, ports open, config written correctly
- [ ] `molecule test` full lifecycle passes (create → converge → idempotence → verify → destroy)
- [ ] `ansible-lint` zero warnings (default profile)
- [ ] Role `README.md` documents all variables with defaults, descriptions, and usage examples
- [ ] Tags applied to all tasks: phase tag (`install`, `configure`, `deploy`) + component tag
- [ ] `meta/main.yml` lists correct platform versions and minimum ansible version
- [ ] CI pipeline runs `ansible-lint` + `molecule test` on PR — both green

## Quick Reference: Common Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| `changed > 0` on idempotence | Task is not idempotent | Use idempotent module, add `when:` condition, or use `creates:` |
| `ansible-lint` FQCN error | Using short module name | Add `ansible.builtin.` prefix |
| `ansible-lint` name error | Missing `name:` or using noun | Add imperative sentence as `name:` |
| Service not running in verify | Handler not triggered or service not enabled | Check `notify:` spelling matches handler name exactly |
| Molecule create fails | Docker not running or wrong image name | Start Docker, verify image tag exists |
