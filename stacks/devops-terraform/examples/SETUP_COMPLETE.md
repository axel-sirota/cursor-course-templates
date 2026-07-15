# Reference Solution - Setup Complete!

## What's Ready

A complete, working Terraform project provisioning an ECS Fargate web service behind an ALB, plus an S3+CloudFront static frontend, using the module layout and session workflow this stack teaches.

### Location
```
examples/aws-ecs-webapp/
```

### Status
- Module tree scaffolded (`vpc`, `alb`, `ecs-service`, `static-site`)
- Provider pinned (`hashicorp/aws ~> 5.0`), Terraform pinned (`>= 1.9, < 2.0.0`)
- Backend configured for S3 with native locking (`use_lockfile = true`)
- `terraform fmt -check -recursive` / `terraform validate` / `tflint` all clean
- `checkov -d .` clean (one documented skip — see `tests/policy/README.md` note)
- Module outputs verified end-to-end (`vpc` -> `alb` -> `ecs-service`)
- Automation script (`scripts/verify_deployment.py`) unit-tested with Stubber, no real AWS calls needed to run the test suite

## Quick Start

```bash
cd examples/aws-ecs-webapp

cp backend.hcl.example backend.hcl
cp terraform.tfvars.example terraform.tfvars
# edit both with your bucket name / project values

terraform init -backend-config=backend.hcl
terraform plan -out=terraform_plans/initial.tfplan
terraform apply terraform_plans/initial.tfplan

terraform output alb_dns_name
```

## Important Notes

### Backend Bootstrap Required First
The S3 state bucket referenced in `backend.hcl` must already exist — this project's own Terraform cannot create the backend it depends on. See `rules/000-environment-setup.mdc` section 5 for the one-time bootstrap commands.

### Region / Naming
- Default region: `us-east-1` (`var.aws_region`)
- Resources named `<project>-<environment>-<resource>`, e.g. `acme-dev-ecs-cluster`
- ALB DNS name is dynamic — always read it from `terraform output alb_dns_name`, never hardcode

### Cost
Rough dev-environment estimate: ~$70-75/month (single NAT gateway, 2 small Fargate tasks, low-traffic ALB + CloudFront). See `vibe/vibe_ecs_service_guide.md` for the full breakdown. Destroy (`terraform destroy`, run manually by a human, never automated) when not actively teaching from this example.

## Architecture

### Module Composition (Root `main.tf` Calls Child Modules Directly)
```hcl
module "vpc" { source = "./modules/vpc" ... }
module "alb" { source = "./modules/alb" ... vpc_id = module.vpc.vpc_id ... }
module "ecs_service" {
  source                = "./modules/ecs-service"
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  target_group_arn      = module.alb.target_group_arn
  alb_security_group_id = module.alb.alb_security_group_id
}
module "static_site" { source = "./modules/static-site" ... }
```

### Key Features
- Execution role vs. task role IAM separation (least privilege)
- `terraform_remote_state`-free composition (single project, direct module outputs)
- `default_tags` provider block — every resource auto-tagged with `Project`/`Environment`/`ManagedBy`
- `deployment_circuit_breaker` on the ECS service (auto-rollback on failed deploys)
- `lifecycle { prevent_destroy = true }` on the S3 static-assets bucket

## API / Outputs Surface

### Root Outputs
- `vpc_id`, `private_subnet_ids`, `public_subnet_ids`
- `alb_dns_name`
- `ecs_cluster_name`, `ecs_service_name`
- `cloudfront_domain_name`

### Automation CLI
- `scripts/verify_deployment.py --cluster <name> --service <name>` — polls ECS until steady state or timeout

## Testing

### Run Tests
```bash
cd examples/aws-ecs-webapp
.venv/bin/python3 -m pytest tests/ -v -m "not e2e"
```

### Test Files
- `tests/policy/check_alb_https_redirect.py` — checkov custom check
- `tests/scripts/test_verify_deployment.py` — HP/UP unit tests via Stubber
- `tests/integration/test_e2e_stack.py` — e2e apply/destroy (marked `e2e`, run manually)
- `tests/README.md` — how to run each layer

## Teaching With This Solution

### Show Students
1. **Module boundaries by blast radius** — `vpc` (rarely changes) vs. `ecs-service` (changes per deploy)
2. **Plan-before-apply discipline** — every `apply` in this example's history came from a saved `.tfplan`
3. **Validation-first checks** — the checkov custom check written before the ALB listener existed
4. **Least-privilege IAM** — execution role vs. task role split
5. **CI/CD with OIDC** — `.github/workflows/terraform.yml`, no static AWS keys anywhere

### Key Files to Reference
- `main.tf` — module composition and wiring
- `modules/ecs-service/main.tf` — task definition, service, IAM roles
- `modules/vpc/main.tf` — subnet/routing/NAT pattern
- `tests/policy/check_alb_https_redirect.py` — validation-first example
- `.github/workflows/terraform.yml` — full CI/CD pipeline

## Stopping / Tearing Down

```bash
# Only ever run by a human, deliberately — never automated
terraform plan -destroy -out=terraform_plans/teardown.tfplan
terraform apply terraform_plans/teardown.tfplan
```

## Troubleshooting

### `terraform init` fails with backend errors
- Confirm the S3 bucket in `backend.hcl` exists and you have access (`aws s3 ls s3://<bucket>`)
- Confirm your AWS profile/role has `s3:GetObject`/`PutObject`/`ListBucket` on the state bucket

### `terraform plan` shows unexpected changes on a clean checkout
- Run `terraform init -upgrade` to make sure `.terraform.lock.hcl`-pinned provider versions match what's installed
- Check for local, uncommitted `.tfvars` differences

### ALB target group shows unhealthy targets
- Check `scripts/verify_deployment.py --cluster <name> --service <name>` output
- Check the ECS service's CloudWatch log group for container startup errors
- Confirm the security group rule allows the ALB's security group as an ingress source on the container port

## Next Steps

1. Review `plan/architecture/` docs (if generated) for the design rationale
2. Walk through one complete session: VPC apply -> ALB+ECS apply -> curl the DNS name
3. Use as reference during teaching
4. Show students the validation-first checkov check and its RED -> GREEN cycle

## Perfect for Teaching

This solution demonstrates:
- Professional Terraform module structure
- Plan-before-apply discipline, session by session
- Validation-first (checkov/tflint/pytest) development
- Least-privilege IAM
- CI/CD with OIDC, no static credentials
- Complete documentation

**Ready to use as a teaching reference.**
