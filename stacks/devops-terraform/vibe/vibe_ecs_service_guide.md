# ECS Fargate + ALB + Static Site — Domain Example Guide

## Purpose & Scope

Full domain walkthrough for this stack's worked reference example: an ECS Fargate service behind an Application Load Balancer, with an S3 + CloudFront static frontend. This is the Terraform analog of the reference stack's chatbot domain guide.

**Related Documents:**
- [ecs-service-variables.md](../templates/ecs-service-variables.md) — the variables.tf contract
- [ecs-service-main.md](../templates/ecs-service-main.md) — the resource blocks
- [ecs-service-networking.md](../templates/ecs-service-networking.md) — VPC/ALB "data layer"
- [ecs-service-tests.md](../templates/ecs-service-tests.md) — checkov/tflint/pytest+moto/e2e tests
- [ecs-service-providers.md](../templates/ecs-service-providers.md) — provider/version pinning
- [examples/aws-ecs-webapp/](../examples/aws-ecs-webapp/) — the full applied reference project

**When to use this guide:**
- Teaching the full session-based build of a realistic multi-tier AWS architecture
- Explaining module boundary decisions during a live session
- Debugging a student's divergence from the reference

## Entities

| Entity | Module | Purpose |
|--------|--------|---------|
| VPC | `modules/vpc` | Network foundation — public/private subnets, routing, NAT |
| ALB | `modules/alb` | Public entry point, TLS termination, HTTP→HTTPS redirect |
| Target Group | `modules/alb` | Health-checked pool of ECS task IPs the ALB forwards to |
| ECS Cluster | `modules/ecs-service` | Logical grouping for Fargate tasks |
| Task Definition | `modules/ecs-service` | Container spec: image, CPU/memory, env, secrets, logging |
| ECS Service | `modules/ecs-service` | Keeps N tasks running, registers/deregisters with the target group |
| S3 Bucket (static assets) | `modules/static-site` | Origin for the CloudFront distribution |
| CloudFront Distribution | `modules/static-site` | CDN in front of the S3 origin, HTTPS via ACM |

## Relationships / Dependency Graph

```
                    ┌────────────┐
                    │    VPC      │
                    └──────┬─────┘
                            │ vpc_id, subnet_ids
              ┌─────────────┼──────────────┐
              ▼                             ▼
        ┌──────────┐                 ┌─────────────┐
        │   ALB     │                 │ static-site │
        └─────┬────┘                 │ (S3 + CF)    │
              │ target_group_arn,      └─────────────┘
              │ alb_security_group_id      (independent —
              ▼                             no ECS dependency)
        ┌──────────────┐
        │ ecs-service   │
        └──────────────┘
```

`ecs-service` depends on both `vpc` (subnets, security-group source) and `alb` (target group ARN). `static-site` depends only on `vpc` if it needs a private origin-access setup — for a public CDN-fronted bucket it has no VPC dependency at all, which is why it can be built in a separate, parallelizable session.

## Variables/Outputs Contract Design Decisions

- **`vpc_id` and `private_subnet_ids` are plain inputs to `ecs-service`**, not resolved internally — this keeps `ecs-service` reusable against any VPC (including one it didn't create), which matters if a platform team owns networking separately from the application team.
- **`target_group_arn` is an input, not created inside `ecs-service`** — the ALB module owns the target group because target groups are a routing concern, not a compute concern; this also lets one ALB route to multiple ECS services (blue/green, multiple apps) without duplicating ALB infrastructure.
- **`enable_autoscaling` defaults to `false`** — Phase 2 (Session 3) ships a fixed `desired_count`; autoscaling is an explicit opt-in enhancement, not baked into the base contract, so the skeleton and first real apply stay simple and easy to verify.

## Tagging Strategy

Every resource picks up `local.common_tags` (`Project`, `Environment`, `ManagedBy`) via the `default_tags` provider block, so new resource types are tagged automatically without per-resource tag blocks. Resource-specific tags (e.g. `Name`) are added on top via `merge(local.common_tags, { Name = "..." })`.

## Cost Considerations

Rough monthly estimate for the `dev` environment (single NAT gateway, 2 Fargate tasks at 256 CPU/512 MiB, minimal ALB traffic):

| Resource | Est. Monthly Cost |
|----------|-------------------|
| NAT Gateway (single, dev) | ~$32 + data processing |
| ALB | ~$16 + LCU usage |
| ECS Fargate (2 tasks, 0.25 vCPU/0.5GB) | ~$18 |
| CloudFront + S3 (low traffic) | ~$1-5 |
| **Total (dev)** | **~$70-75/month** |

Production sizing (per-AZ NAT gateways, larger tasks, autoscaling) will cost meaningfully more — generate a real estimate with `infracost breakdown --path .` before committing to a prod session's scope, and note it in that session's summary (`600-phase-transition.mdc` cost-impact section).

## Teaching Flow

1. Walk through `plan/architecture/resources.md` for this example — point out the dependency graph above
2. Show the Phase 0 skeleton: `modules/*/main.tf` with `var.enabled = false` gates, `terraform plan` returning 0 resources
3. Session 2 (VPC): apply, then `aws ec2 describe-subnets` to show real subnets
4. Session 3 (ALB + ECS): apply, then curl the ALB DNS name once tasks are steady
5. Session 4 (static-site): apply, then load the CloudFront URL
6. Session 5 (CI/CD): show the PR-comment plan output, then the manual-approval gate in the GitHub Actions UI

Reference the templates in `templates/ecs-service-*.md` for the exact HCL used at each step — do not improvise different resource shapes mid-session, so students can diff their own work against a stable reference.
