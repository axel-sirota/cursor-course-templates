# Docker for Ops Tooling — Vibe Coding Guide

## Purpose & Scope

When and how to containerize the Python automation CLI (`scripts/`) in this stack, plus the optional pattern for pinning a reproducible Terraform runner image for CI. Reference this guide when a script needs to run outside a developer's local machine.

**Related Documents:**
- [Deploy CI/CD Rule](../rules/501-deploy-cicd.mdc) — the full Dockerfile patterns live here; this guide covers the *when* and *why*
- [Terraform Style Rule](../rules/300-terraform-style.mdc) — Python script style conventions the container image assumes

## When to Containerize

**Do containerize** `scripts/deploy.py` / `scripts/verify_deployment.py` when:
- The script runs as a scheduled ECS task (e.g. a nightly drift-check or a cost-report job)
- The script needs to run identically across every engineer's machine and CI, and `pip install` drift has caused problems before
- The script is invoked from a Lambda-backed automation (via a container-image Lambda)

**Do NOT containerize**:
- Terraform itself, for local development — engineers run `terraform` directly via `tfenv`, not through Docker; wrapping every `terraform plan` in `docker run` adds friction (volume-mounting AWS credentials, slower iteration, an extra layer to debug) for no real benefit in local dev
- A one-off script an engineer runs manually from their own `.venv`

## Ops CLI Image (When Containerizing Is Warranted)

Multi-stage, `python:3.11-slim`, non-root user, entrypoint is the Click command — same rigor as an application-server Dockerfile, but shaped for a CLI, not a service:

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY scripts/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN useradd --create-home --shell /bin/bash ops
USER ops
COPY --from=builder /root/.local /home/ops/.local
COPY --chown=ops:ops scripts/ .
ENV PATH=/home/ops/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "deploy.py"]
```

Notable differences from an app-server image: no `EXPOSE`, no `HEALTHCHECK` (nothing is listening — this runs, does work, exits), and the `ENTRYPOINT` is the CLI command rather than `uvicorn`/`gunicorn`.

## Optional: Pinned Terraform Runner for CI Reproducibility

Only if the course wants to demonstrate fully pinned, containerized CI runners (useful when CI infrastructure can't use `tfenv`/`setup-terraform` directly, e.g. self-hosted runners with strict image allowlists):

```dockerfile
FROM hashicorp/terraform:1.9.8
RUN apk add --no-cache python3 py3-pip aws-cli
WORKDIR /workspace
ENTRYPOINT ["terraform"]
```

Tell students explicitly: **this is an optional reproducibility pattern for CI runners, not the normal way to invoke Terraform.** `hashicorp/setup-terraform` (as used in `templates/ci-pipeline-template.yml`) is the default, simpler CI pattern.

## Out of Scope Here: Application Containers

If the infrastructure this stack deploys is itself a containerized application (e.g. the ECS Fargate service in `examples/aws-ecs-webapp`), that application's own `Dockerfile` belongs to **whatever app-stack module built it** (e.g. `stacks/python-fastapi` or `stacks/node-service`), not to this stack. `devops-terraform` only consumes a pre-built image from ECR (`var.ecr_repository_url` + `var.image_tag`) — it does not define how that image is built.

## `.dockerignore` for the Ops CLI Image

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
tests/
.terraform/
*.tfstate*
terraform_plans/
.git/
```

## Anti-Patterns to Avoid

- Wrapping local `terraform plan`/`apply` in Docker "for consistency" when `tfenv` already solves version pinning with far less friction
- Baking AWS credentials into the ops CLI image instead of injecting them at runtime (env vars, mounted credentials, or an ECS task role)
- Using the ops CLI image's Python version as the source of truth for local dev — `scripts/requirements.txt` + `.venv` is
- Building the application's own Dockerfile inside this stack's `examples/` — reference it, don't duplicate it
