# Session 9 — New Stack: `devops-ansible`

**Phase:** 3 — Group B (devops persona)
**Parallel with:** Sessions 7, 8, 10–12
**Depends on:** Sessions 1–6 complete
**Client fit:** Any enterprise team doing server configuration management, post-provision setup

## Architecture Shape
IaC Playbook — Ansible roles and playbooks for configuration management. Not provisioning (that's Terraform). Configures what Terraform created.

---

## Files to Create

```
stacks/devops-ansible/
├── context.md
├── rules/
│   ├── 000-ansible-workflow.mdc
│   ├── 100-ansible-architecture.mdc
│   ├── 200-ansible-testing.mdc
│   └── 300-ansible-style.mdc
├── templates/
│   ├── ansible-starter.md
│   ├── phase-checklist.md
│   └── molecule/
│       └── default/
│           ├── molecule.yml
│           └── verify.yml
├── vibe/
│   ├── vibe_architecture.md
│   └── vibe_development_lifecycle.md   (references stacks/shared/)
└── examples/
    └── nginx-role/
        ├── tasks/main.yml
        ├── handlers/main.yml
        ├── defaults/main.yml
        ├── meta/main.yml
        └── molecule/default/
            ├── molecule.yml
            ├── converge.yml
            └── verify.yml
```

---

## File Specifications

### `context.md`

```markdown
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

## Active Phase
- Current: Phase 0 (Skeleton)
```

### `rules/000-ansible-workflow.mdc`

- **Role-first**: create role structure before writing tasks. `ansible-galaxy role init {rolename}`.
- **Molecule test loop**: write failing Molecule verify → implement task → `molecule test` green.
- **CI gate**: `ansible-lint` → `molecule test` (Docker driver) → PR merge.
- **Idempotency gate**: Molecule runs the role twice; second run must show zero `changed` tasks.
- **Vault for secrets**: `ansible-vault encrypt_string` for any secret. Never commit plaintext passwords or API keys.

### `rules/100-ansible-architecture.mdc`

- **Role structure**: every role uses full directory structure: `tasks/`, `handlers/`, `defaults/`, `vars/`, `files/`, `templates/`, `meta/`, `molecule/`.
- **One responsibility per role**: a role that installs AND configures AND deploys is three roles. Compose them in a playbook.
- **defaults vs vars**: `defaults/main.yml` for values users should override. `vars/main.yml` for internal values that should not be overridden. Never define configurable values in tasks.
- **Handlers for restarts**: `notify: restart nginx`. Never `ansible.builtin.service` state=restarted in a task — it runs every time, breaking idempotency.
- **Become discipline**: use `become: true` only on tasks that require it. Not on the entire play unless all tasks need root.
- **Tags**: tag tasks by phase (`install`, `configure`, `deploy`) and by component. Allows targeted runs.
- **No shell/command modules for idempotent work**: use specific modules (`package`, `file`, `template`, `service`). Use `shell`/`command` only when no module exists; add `changed_when: false` or a proper condition.

### `rules/200-ansible-testing.mdc`

- **Molecule is mandatory**: every role has a `molecule/default/` directory before any task is written.
- **Test lifecycle**: `molecule create` → `molecule converge` → `molecule idempotence` → `molecule verify` → `molecule destroy`. All phases pass.
- **Idempotence test**: Molecule's built-in idempotence check runs the role twice and fails if `changed > 0` on the second run.
- **Verify with Testinfra or Ansible**: `molecule verify` runs assertions. Prefer Ansible verify tasks (`assert`, `stat`, `command`) for simplicity. Use Testinfra (Python) for complex assertions.
- **Docker driver for most roles**: fast iteration. Use `image: geerlingguy/docker-ubuntu2404-ansible` or similar pre-configured image.
- **Vagrant driver**: only for roles that need systemd, kernel modules, or real network interfaces.

### `rules/300-ansible-style.mdc`

- **Task names are imperative sentences**: `"Install nginx package"` not `"nginx"`. Always present tense imperative.
- **YAML formatting**: 2-space indent. No tabs. `ansible-lint` enforces.
- **Fully qualified collection names (FQCN)**: `ansible.builtin.package` not `package`. Required in `ansible-lint` default profile.
- **`no_log: true`** on tasks that handle secrets (`ansible.builtin.user` with password, `ansible.builtin.uri` with auth headers).
- **`loop` over `with_items`**: use `loop:` syntax (modern). `with_items` is legacy.
- **Variable naming**: `{rolename}_{variable}` prefix for all role variables to avoid collisions: `nginx_port`, `nginx_worker_processes`.

### `templates/ansible-starter.md`

Scaffold for a new role:
```
roles/
  {rolename}/
    tasks/
      main.yml        (import_tasks or direct tasks)
      install.yml     (tagged install tasks)
      configure.yml   (tagged configure tasks)
    handlers/
      main.yml        (service restart handlers)
    defaults/
      main.yml        (all configurable defaults)
    vars/
      main.yml        (internal non-overridable vars)
    files/
      (static files to copy)
    templates/
      {config}.j2     (Jinja2 templates)
    meta/
      main.yml        (dependencies, galaxy info)
    molecule/
      default/
        molecule.yml
        converge.yml
        verify.yml
```

Include example `tasks/main.yml` showing idempotent package install + handler notify.
Include example `defaults/main.yml` with `{rolename}_` prefixed variables.

### `templates/molecule/default/molecule.yml`

```yaml
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: geerlingguy/docker-ubuntu2404-ansible
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible
```

### `templates/molecule/default/verify.yml`

```yaml
- name: Verify
  hosts: all
  gather_facts: false
  tasks:
    - name: Assert service is running
      ansible.builtin.service_facts:
    - name: Check {service} is active
      ansible.builtin.assert:
        that:
          - ansible_facts.services['{service}.service'].state == 'running'
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] Role structure initialized (`ansible-galaxy role init`)
- [ ] `molecule/default/` directory created with molecule.yml + converge.yml + verify.yml
- [ ] `molecule create` succeeds
- [ ] `ansible-lint` passes on empty skeleton

**Phase 1+ — Implementation:**
- [ ] `molecule converge` succeeds (tasks run without error)
- [ ] `molecule idempotence` passes (zero changed on second run)
- [ ] All configurable values in `defaults/main.yml` with `{rolename}_` prefix
- [ ] Service restarts via handlers, not tasks
- [ ] No secrets in plaintext vars

**Handoff:**
- [ ] `molecule verify` passes (service running, ports open, config correct)
- [ ] `molecule test` full lifecycle passes
- [ ] `ansible-lint` zero warnings
- [ ] Role README documents all variables with defaults and examples

### `vibe/vibe_architecture.md`

- **Ansible vs Terraform**: Terraform creates resources (VMs, networks, databases). Ansible configures what runs on them (installs packages, writes config files, starts services). They are complementary. Ansible should not provision VMs; Terraform should not configure OS packages.
- **Role design philosophy**: a role that does one thing is testable, reusable, and composable. A role that does everything is a monolith. Decompose early.
- **Idempotency is not optional**: every task must be safe to run multiple times. This is the fundamental contract of Ansible. Non-idempotent tasks are bugs.
- **When Ansible vs Chef/Puppet**: Ansible is agentless (SSH-based), YAML-declarative, lower learning curve. Choose Ansible for teams that don't already have Chef/Puppet. Chef/Puppet have advantages at very large scale (>1000 nodes) with convergence loops.
- **Push vs pull**: Ansible is push (you run it from a control node). Puppet/Chef are pull (agents check in). For CI/CD triggered deployments, push is simpler. For continuously-converging fleet management, pull has advantages.

### `vibe/vibe_development_lifecycle.md`

References `stacks/shared/`. Adds Ansible-specific:
- Molecule-first development loop
- `ansible-lint` in pre-commit hooks
- Vault rotation discipline: rotate secrets, re-encrypt vault, test

### `examples/nginx-role/`

Five files showing a complete, Molecule-tested nginx installation role:
- `tasks/main.yml` — install + configure + enable nginx with proper handler notify
- `handlers/main.yml` — restart nginx handler
- `defaults/main.yml` — `nginx_port: 80`, `nginx_worker_processes: auto`, etc.
- `meta/main.yml` — galaxy info, no dependencies
- `molecule/default/molecule.yml` + `converge.yml` + `verify.yml` — full Molecule setup that verifies nginx is running and responding on configured port

---

## Acceptance Criteria

- [ ] `ls stacks/devops-ansible/rules/` shows 4 files
- [ ] `ls stacks/devops-ansible/templates/` shows `ansible-starter.md`, `phase-checklist.md`, `molecule/`
- [ ] `ls stacks/devops-ansible/vibe/` shows 2 docs
- [ ] `ls stacks/devops-ansible/examples/nginx-role/` shows role structure with molecule/
- [ ] `context.md` Architecture Shape = "IaC Playbook"
- [ ] `rules/200-ansible-testing.mdc` contains "molecule idempotence" rule
- [ ] `vibe_architecture.md` contains "Ansible vs Terraform" section
- [ ] `rules/100-ansible-architecture.mdc` contains "Handlers for restarts" rule
