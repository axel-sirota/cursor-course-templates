# Phase-Based Infrastructure Workflow Guide

## Purpose & Scope

This guide provides rules, patterns, and instructions for AI coding assistants (Claude Code, Cursor, etc.) working on Terraform-based infrastructure projects. Reference this document when planning, scaffolding, or implementing any phase of an infrastructure build.

**Related Documents:**
- [Terraform Boilerplate Guide](vibe_terraform_boilerplate.md) — project structure and file-by-file walkthrough
- [State Management Guide](vibe_state_management.md) — remote state, locking, cross-module references
- [Deploy Lifecycle Guide](vibe_deploy_lifecycle.md) — Git/CI workflow for infra changes
- [ECS Service Guide](vibe_ecs_service_guide.md) — the domain worked example this workflow builds toward

**When to use this guide:**
- Starting a brand-new infrastructure project
- Deciding module boundaries before writing HCL
- Planning the session-by-session build order
- Understanding what belongs in Phase 0 vs. Phase N

## Core Principles

1. **Contract-First**: Design `variables.tf`/`outputs.tf` before resource blocks — the Terraform analog of API-first design.
2. **Plan-Only Skeleton**: Phase 0 proves the whole module tree type-checks and plans cleanly, with zero real resources created.
3. **One Module Per Session**: Each Phase 1+ session applies exactly one module or tightly-coupled resource group.
4. **Validation-First**: A failing checkov/tflint/pytest+boto3 check exists before real resource blocks are written.
5. **Never Apply Without a Saved Plan**: Every `apply` runs against a reviewed `terraform_plans/*.tfplan` file.
6. **Blast-Radius Ordering**: Low-churn, high-blast-radius modules (networking) are built and stabilized before high-churn, low-blast-radius modules (application, CI/CD).

## Phase Structure Quick Reference

```
Architect Phase   -> design module contracts, no .tf files
Phase 0 (Skeleton) -> scaffold all modules, terraform plan only, no apply
Phase 1            -> modules/vpc (networking foundation)
Phase 2            -> modules/alb + modules/ecs-service (compute + routing)
Phase 3            -> modules/static-site (S3 + CloudFront frontend)
Phase 4            -> CI/CD pipeline wiring (OIDC role, GitHub Actions)
Phase Transition    -> session summary after each phase
```

## Full Worked Session Table

| Session | Phase | Module(s) | Depends On | Deliverable |
|---------|-------|-----------|------------|-------------|
| 1 | Phase 0 | All (skeleton) | — | Full tree scaffolded, `terraform plan` succeeds, 0 resources |
| 2 | Phase 1 | `modules/vpc` | Session 1 | VPC, subnets, routing, NAT applied |
| 3 | Phase 2 | `modules/alb` + `modules/ecs-service` | Session 2 (VPC outputs) | ALB, target group, ECS cluster + Fargate service applied, ALB DNS reachable |
| 4 | Phase 3 | `modules/static-site` | Session 2 (VPC outputs, if needed) | S3 bucket + CloudFront distribution applied, frontend reachable |
| 5 | Phase 4 | CI/CD wiring | Session 3 (needs cluster/service names for smoke checks) | OIDC IAM role, GitHub Actions workflow applying on `main` |

Each row is a separate session. Do not combine rows. Do not skip a row's validation-first check.

## Session Anatomy (Every Phase 1+ Session)

1. **Review** — read the session plan and previous session's summary
2. **RED** — write the validation-first check; confirm it fails against the skeleton
3. **Contract check** — confirm `variables.tf`/`outputs.tf` match the architect-phase design; do not silently change them
4. **GREEN** — flesh out real resource blocks
5. **Plan** — `terraform plan -out=terraform_plans/<ts>.tfplan`; review the diff for scope creep
6. **Apply** — `terraform apply terraform_plans/<ts>.tfplan`
7. **Verify** — validation check now passes; post-apply boto3/aws-cli check confirms real health
8. **REFACTOR** — extract `locals`, switch `count` to `for_each` where it improves resilience, tighten variable `validation` blocks
9. **Transition** — generate `plan/sessions/session-N-summary.md`; STOP and wait for explicit "Start Session N+1"

## Why This Order (Blast-Radius Reasoning)

- **VPC first**: everything else depends on subnet IDs; VPC changes are rare once stable, and getting CIDR math wrong early is cheap to fix before anything else references it.
- **ALB + ECS together**: a target group with no service, or a service with no target group, is a broken intermediate state — apply them in the same session.
- **Static site independent**: `modules/static-site` (S3 + CloudFront) has no hard dependency on ECS; it can be built in parallel with Phase 2 in a real team, but for a single-session-at-a-time course workflow it's sequenced after to keep sessions focused.
- **CI/CD last**: the pipeline's smoke check needs real cluster/service names to verify against, so it depends on Phase 2's outputs existing.

## Anti-Patterns to Avoid

- Applying Phase 2 before Phase 1's VPC outputs are stable (forces a destroy/recreate of subnets mid-session)
- Writing real resource blocks before the validation-first check
- Combining VPC and ECS into one module "to save a session" — couples unrelated blast radii
- Skipping the Phase 0 skeleton and going straight to real resources — loses the contract-validation safety net
- Auto-advancing to the next session without an explicit user go-ahead

## Quick Reference: Commands Per Session Stage

```bash
# RED (before real resources exist)
checkov -d . --external-checks-dir tests/policy --check CKV_ACME_1   # expect FAIL

# GREEN
terraform fmt -recursive
terraform validate
tflint
terraform plan -out=terraform_plans/$(date +%Y%m%d%H%M%S).tfplan
terraform apply terraform_plans/<timestamp>.tfplan

# Verify
checkov -d . --external-checks-dir tests/policy --check CKV_ACME_1   # expect PASS
aws ecs describe-services --cluster acme-dev-cluster --services acme-dev-web

# REFACTOR (still green)
terraform plan   # expect "No changes"
```
