# Architecture Vibe: Terraform IaC

## What Terraform is for

Terraform provisions infrastructure — it creates, updates, and destroys cloud resources. It does not configure what runs on those resources. That distinction matters: Terraform creates an EC2 instance; Ansible configures the OS on it. Terraform creates an EKS cluster; Helm deploys applications into it.

Infrastructure should be cattle, not pets. Resources are defined declaratively and replaced when they drift, not nursed back to health. Prefer immutable infrastructure: when a configuration needs to change, replace the resource rather than modifying it in place.

## Module design philosophy

Modules should be small, focused, and composable. A module that provisions a VPC should know nothing about the applications that will run in it. A module that creates an RDS instance should not also create the VPC, the security groups, and the IAM roles — those are separate concerns and separate modules.

If a module does five things, it should be five modules. The right question is: "can I use this module in a context where I don't need the other things it does?" If the answer is no, it's doing too much.

Root modules (the `envs/` directories) compose child modules. Child modules should never call other child modules more than one level deep — deep nesting creates brittle dependency chains.

## When to use workspaces vs directories

Use **workspaces** only when environments are truly identical in topology — same resources, same structure, only variable values differ. A workspace is just a different state file; it is not a different configuration.

Use **directories** (`envs/dev/`, `envs/staging/`, `envs/prod/`) when environments have genuinely different topologies: prod has a multi-AZ RDS cluster, dev has a single-AZ instance; prod has a WAF, dev does not. Directory-per-environment makes those differences explicit in code rather than buried in variable files.

When in doubt, use directories. Workspaces make it too easy to accidentally apply dev changes to prod.

## When to reach for Terragrunt

Reach for Terragrunt only when you have four or more environments with identical structure and the DRY pain is genuinely significant — repeated backend configs, repeated provider blocks, repeated module calls with only variable values changing. Terragrunt solves real repetition at scale.

Do not introduce Terragrunt prematurely. Two or three environments with slight differences are handled fine with plain Terraform and directory-per-environment. Adding Terragrunt to a small project adds toolchain complexity without proportional benefit.

## Terraform vs Ansible

Terraform creates resources. Ansible configures what is running on them. Never configure OS-level settings, install packages, or manage files on running instances using Terraform. Use `user_data` scripts sparingly and only for bootstrapping — anything complex belongs in Ansible or a configuration management tool.

If you find yourself writing long `user_data` blocks or using `null_resource` with `local-exec` to run shell commands, stop and ask whether this belongs in Terraform at all.

## Terraform vs Kubernetes / Helm

Terraform creates the Kubernetes cluster (EKS, GKE, AKS). Helm deploys applications into it. Do not manage Kubernetes workloads — Deployments, Services, ConfigMaps, Ingresses — with Terraform `kubernetes_manifest` resources in production environments.

The `kubernetes_manifest` resource and the `helm_release` resource are appropriate for bootstrapping cluster-level infrastructure (cert-manager, ingress controllers, monitoring stacks) when those components are tightly coupled to the cluster lifecycle. They are not appropriate for application deployments that change frequently.

## The state file is sacred

The Terraform state file is the source of truth for what Terraform believes exists in the world. Never delete it. Never edit it manually. If the state drifts from reality, investigate before touching it — use `terraform plan` to understand the extent of the drift, then use `terraform import` or `terraform state mv` to reconcile it carefully.

A corrupted or lost state file means Terraform has forgotten about resources it created. Those resources will not be managed or cleaned up. Treat state corruption as a production incident.
