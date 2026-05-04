# Ansible Role Scaffold

## Initialize a New Role

```bash
ansible-galaxy role init roles/{rolename}
mkdir -p roles/{rolename}/molecule/default
```

## Directory Structure

```
roles/
  {rolename}/
    tasks/
      main.yml        (import_tasks entry point)
      install.yml     (tagged install tasks)
      configure.yml   (tagged configure tasks)
    handlers/
      main.yml        (service restart handlers)
    defaults/
      main.yml        (all configurable defaults with {rolename}_ prefix)
    vars/
      main.yml        (internal non-overridable vars)
    files/
      (static files to copy with ansible.builtin.copy)
    templates/
      {config}.j2     (Jinja2 templates for ansible.builtin.template)
    meta/
      main.yml        (galaxy_info, dependencies list)
    molecule/
      default/
        molecule.yml  (driver, platforms, provisioner config)
        converge.yml  (playbook that applies the role)
        verify.yml    (assertions about end state)
```

## Example `tasks/main.yml`

```yaml
---
- name: Include install tasks
  ansible.builtin.import_tasks: install.yml
  tags: [install, {rolename}]

- name: Include configure tasks
  ansible.builtin.import_tasks: configure.yml
  tags: [configure, {rolename}]
```

## Example `tasks/install.yml`

```yaml
---
- name: Install {rolename} package
  ansible.builtin.package:
    name: "{{ {rolename}_package_name }}"
    state: present
  become: true
  tags: [install, {rolename}]
```

## Example `tasks/configure.yml`

```yaml
---
- name: Write {rolename} configuration file
  ansible.builtin.template:
    src: {rolename}.conf.j2
    dest: "{{ {rolename}_config_path }}"
    owner: root
    group: root
    mode: "0644"
  become: true
  notify: restart {rolename}
  tags: [configure, {rolename}]

- name: Enable and start {rolename} service
  ansible.builtin.service:
    name: "{{ {rolename}_service_name }}"
    enabled: true
    state: started
  become: true
  tags: [configure, {rolename}]
```

## Example `handlers/main.yml`

```yaml
---
- name: restart {rolename}
  ansible.builtin.service:
    name: "{{ {rolename}_service_name }}"
    state: restarted
  become: true
```

## Example `defaults/main.yml`

```yaml
---
# Package and service names (override for different distros)
{rolename}_package_name: {rolename}
{rolename}_service_name: {rolename}
{rolename}_config_path: /etc/{rolename}/{rolename}.conf

# Network settings
{rolename}_port: 80
{rolename}_bind_address: "0.0.0.0"

# Performance tuning
{rolename}_worker_processes: auto
{rolename}_worker_connections: 1024

# Logging
{rolename}_log_level: warn
{rolename}_access_log: /var/log/{rolename}/access.log
{rolename}_error_log: /var/log/{rolename}/error.log
```

## Example `meta/main.yml`

```yaml
---
galaxy_info:
  author: your_name
  description: Install and configure {rolename}
  license: MIT
  min_ansible_version: "2.16"
  platforms:
    - name: Ubuntu
      versions:
        - jammy
        - noble
    - name: EL
      versions:
        - "9"
  galaxy_tags:
    - {rolename}
    - web
    - server

dependencies: []
```

## Example `molecule/default/molecule.yml`

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

## Example `molecule/default/converge.yml`

```yaml
---
- name: Converge
  hosts: all
  gather_facts: true

  roles:
    - role: {rolename}
```

## Example `molecule/default/verify.yml`

```yaml
---
- name: Verify
  hosts: all
  gather_facts: false

  tasks:
    - name: Gather service facts
      ansible.builtin.service_facts:

    - name: Assert {rolename} service is running
      ansible.builtin.assert:
        that:
          - ansible_facts.services['{rolename}.service'].state == 'running'
        fail_msg: "{rolename} service is not running"

    - name: Assert {rolename} is listening on configured port
      ansible.builtin.uri:
        url: "http://localhost:{{ {rolename}_port }}"
        status_code: 200
      register: response
      failed_when: response.status != 200
```

## Molecule Test Commands

```bash
# Full test lifecycle
molecule test

# Iterative development (keeps container running)
molecule create
molecule converge
molecule idempotence   # Must show changed=0
molecule verify
molecule destroy

# Lint before testing
ansible-lint roles/{rolename}/
```
