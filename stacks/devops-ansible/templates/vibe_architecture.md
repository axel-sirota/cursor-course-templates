# Ansible Architecture Vibe

## Ansible vs Terraform

Terraform creates resources (VMs, networks, databases, load balancers). Ansible configures what runs on them (installs packages, writes config files, starts services, creates users). They are complementary tools, not competitors.

- **Terraform** = "what infrastructure exists"
- **Ansible** = "what software runs on that infrastructure and how it is configured"

Ansible should not provision VMs — use Terraform for that. Terraform should not configure OS packages or application settings — use Ansible for that. The handoff point is: Terraform outputs inventory data (IP addresses, hostnames), Ansible reads that inventory and configures the servers.

## Role Design Philosophy

A role that does one thing is testable, reusable, and composable. A role that does everything is a monolith.

**Decompose early.** It is far easier to start with three small roles and compose them than to split a monolithic role later. Ask: if I wanted to use only the installation part of this role without the configuration, could I? If the answer is no, split the role.

Good decomposition:
- `nginx_install` — installs the nginx package, nothing else
- `nginx_configure` — writes nginx.conf and vhost configs from templates
- `nginx_tls` — manages TLS certificates via Let's Encrypt or cert copy

Bad design: one `nginx` role that installs, configures, manages TLS, creates vhosts, and sets up monitoring.

## Idempotency is Not Optional

Every task must be safe to run multiple times. Running the same playbook twice must produce the same result — no extra service restarts, no overwritten files with identical content, no duplicate cron jobs.

This is the fundamental contract of Ansible. Non-idempotent tasks are bugs, not features.

Testing for idempotency with Molecule (`molecule idempotence`) is mandatory. A role that fails the idempotence check is not ready to merge.

## Ansible vs Chef/Puppet

Ansible is agentless (SSH-based), YAML-declarative, and has a low learning curve. Choose Ansible for:
- Teams that don't already have Chef/Puppet expertise
- Organizations that want low operational overhead (no agent fleet to manage)
- Smaller to medium infrastructure (under ~500 nodes)
- CI/CD-triggered configuration management

Chef/Puppet have advantages at very large scale (1000+ nodes) with continuous convergence loops — agents check in on a schedule and self-correct drift. For continuously-converging fleet management at scale, pull-based agents have architectural advantages.

## Push vs Pull Model

Ansible is **push**: you run `ansible-playbook` from a control node, and it pushes changes over SSH to target hosts.

Puppet/Chef are **pull**: agents on each host check in to a central server, receive their catalog, and converge themselves.

For CI/CD-triggered deployments, push is simpler — your pipeline runs the playbook, you see the output immediately. For continuously-converging fleet management where you want servers to self-heal configuration drift between pipeline runs, pull-based systems have architectural advantages.

Most teams starting with configuration management should use Ansible push. Graduate to pull-based agents only if continuous convergence at scale becomes a real operational requirement.

## Inventory Strategy

- **Static YAML inventory**: good for small, stable environments. Checked into version control alongside playbooks.
- **Dynamic inventory (AWS EC2 plugin)**: generates inventory from live AWS tags at runtime. Required for auto-scaling groups. Configuration lives in `inventory/aws_ec2.yml`.
- **Terraform outputs → Ansible inventory**: use `terraform output -json` piped into a dynamic inventory script, or use the `cloud.terraform` collection.

Never hardcode IP addresses in playbooks. Always use inventory groups and variables.
