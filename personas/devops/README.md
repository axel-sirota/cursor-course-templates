# DevOps Persona

Activates IaC-focused workflow for Terraform, Ansible, and Kubernetes/Helm.

## Setup

```
/set-persona devops
/setup-stack          # choose: devops-terraform, devops-ansible, devops-k8s-helm
/start-session
```

## What gets installed

- `rules/000-devops-workflow.mdc` — plan-before-apply, idempotency, no-secrets rules
- `agents/iac-reviewer.md` — security and drift review for IaC changes
- `hooks.json` — lint IaC on file edit, block destructive shell commands

## Available stacks

| Stack | Use for |
|-------|---------|
| `devops-terraform` | Cloud infrastructure (AWS/GCP/Azure modules) |
| `devops-ansible` | Server configuration management |
| `devops-k8s-helm` | Kubernetes GitOps with Helm + ArgoCD |
