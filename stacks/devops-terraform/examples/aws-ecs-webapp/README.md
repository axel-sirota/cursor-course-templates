# aws-ecs-webapp

Reference Terraform project: a VPC, an ECS Fargate service behind an Application Load Balancer, and an S3 + CloudFront static frontend.

## Prerequisites

- Terraform >= 1.9, < 2.0.0 (or OpenTofu >= 1.7)
- AWS CLI configured (`aws configure` or `AWS_PROFILE` set)
- An existing S3 bucket for remote state (see `rules/000-environment-setup.mdc` in the parent stack for the one-time bootstrap commands)
- An ACM certificate ARN for the ALB's HTTPS listener
- An ECR repository with a pushed image (or point `ecr_repository_url`/`image_tag` at an existing public-ish placeholder image for a dry run)

## Setup

```bash
cp backend.hcl.example backend.hcl
cp terraform.tfvars.example terraform.tfvars
# edit both files with your real bucket name / account values

terraform init -backend-config=backend.hcl
```

## Plan and Apply

```bash
terraform fmt -check -recursive
terraform validate
tflint
checkov -d . --external-checks-dir tests/policy

terraform plan -out=terraform_plans/$(date +%Y%m%d%H%M%S).tfplan
terraform apply terraform_plans/<the-file-above>.tfplan
```

## Verify

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/python3 -m pip install -r scripts/requirements.txt

.venv/bin/python3 scripts/verify_deployment.py \
  --cluster "$(terraform output -raw ecs_cluster_name)" \
  --service "$(terraform output -raw ecs_service_name)"

curl -I "https://$(terraform output -raw alb_dns_name)/health"
```

## Test

```bash
.venv/bin/python3 -m pytest tests/ -v -m "not e2e"
```

See `tests/README.md` for the full layer breakdown, including the optional (paid) e2e suite.

## Module Structure

```
modules/
├── vpc/           # networking foundation
├── alb/           # load balancer + target group + listeners
├── ecs-service/   # ECS cluster, task definition, service, IAM roles
└── static-site/   # S3 + CloudFront frontend
```

## Tear Down

```bash
terraform plan -destroy -out=terraform_plans/teardown.tfplan
terraform apply terraform_plans/teardown.tfplan
```

Always run destroy deliberately, by hand — never scripted or automated.

## Related Documentation

- `../../vibe/vibe_ecs_service_guide.md` — full domain walkthrough
- `../../templates/ecs-service-*.md` — the templated HCL this project implements
- `../SETUP_COMPLETE.md` — teacher-facing status and teaching notes
