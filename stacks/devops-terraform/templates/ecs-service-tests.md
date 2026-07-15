# ECS Service Domain Example: Tests Template

Validation-first checks for the ECS Fargate + ALB worked example — checkov policy checks, tflint, pytest+moto for the automation scripts, and a Terratest-style/pytest integration test for a real apply/destroy cycle.

## 1. checkov Custom Check — ALB HTTPS Redirect

```python
# tests/policy/check_alb_https_redirect.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ALBHttpsRedirect(BaseResourceCheck):
    """Ensure the ALB's HTTP (port 80) listener redirects to HTTPS, never forwards plaintext."""

    def __init__(self):
        super().__init__(
            name="Ensure ALB HTTP listener redirects to HTTPS",
            id="CKV_ACME_1",
            categories=[CheckCategories.NETWORKING],
            supported_resources=["aws_lb_listener"],
        )

    def scan_resource_conf(self, conf):
        if conf.get("port") == [80]:
            actions = conf.get("default_action", [{}])
            if actions and actions[0].get("type") == ["redirect"]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.PASSED


check = ALBHttpsRedirect()
```

Run against the skeleton first — it MUST fail (no `aws_lb_listener` exists yet, or it exists with `count = 0`):
```bash
checkov -d . --external-checks-dir tests/policy --check CKV_ACME_1
```

## 2. tflint — Built-In AWS Ruleset

```hcl
# .tflint.hcl
plugin "aws" {
  enabled = true
  version = "0.32.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "aws_instance_invalid_type" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "terraform_required_version" {
  enabled = true
}
```

## 3. pytest + moto — `scripts/verify_deployment.py`

```python
# tests/scripts/test_HP_verify_deployment_steady_state.py
"""HP: a healthy ECS service reports runningCount == desiredCount."""
from botocore.stub import Stubber
import boto3

from scripts.verify_deployment import get_service_status


def test_HP_verify_deployment_steady_state():
    client = boto3.client("ecs", region_name="us-east-1")
    stubber = Stubber(client)
    stubber.add_response(
        "describe_services",
        {
            "services": [
                {"serviceName": "acme-dev-web", "runningCount": 2, "desiredCount": 2, "status": "ACTIVE"}
            ],
            "failures": [],
        },
        {"cluster": "acme-dev-cluster", "services": ["acme-dev-web"]},
    )
    stubber.activate()

    status = get_service_status(
        cluster="acme-dev-cluster", service="acme-dev-web", region="us-east-1", client=client
    )

    assert status["running_count"] == status["desired_count"]
    assert status["status"] == "ACTIVE"
```

```python
# tests/scripts/test_UP_verify_deployment_missing_service.py
"""UP: an unknown service name surfaces a clear, typed error, not a raw KeyError."""
import boto3
import pytest
from botocore.stub import Stubber

from scripts.verify_deployment import get_service_status


def test_UP_verify_deployment_missing_service_raises():
    client = boto3.client("ecs", region_name="us-east-1")
    stubber = Stubber(client)
    stubber.add_response(
        "describe_services",
        {"services": [], "failures": [{"arn": "arn:aws:ecs:...", "reason": "MISSING"}]},
        {"cluster": "acme-dev-cluster", "services": ["does-not-exist"]},
    )
    stubber.activate()

    with pytest.raises(ValueError, match="service not found"):
        get_service_status(
            cluster="acme-dev-cluster", service="does-not-exist", region="us-east-1", client=client
        )
```

## 4. pytest+boto3 Post-Apply Verification (Real AWS, Run Manually After Apply)

```python
# tests/scripts/test_smoke_ecs_service_healthy.py
"""smoke: run against real infrastructure after a session's terraform apply."""
import boto3
import pytest


@pytest.mark.smoke
def test_smoke_ecs_service_reaches_steady_state():
    client = boto3.client("ecs", region_name="us-east-1")
    response = client.describe_services(cluster="acme-dev-cluster", services=["acme-dev-web"])
    assert response["services"], "expected the ECS service to exist post-apply"
    service = response["services"][0]
    assert service["runningCount"] == service["desiredCount"]
    assert service["status"] == "ACTIVE"
```

## 5. Terratest-Style / pytest Integration Test (Ephemeral Apply + Destroy)

```python
# tests/integration/test_e2e_ecs_service_end_to_end.py
"""e2e: apply the full VPC + ALB + ECS stack into a throwaway workspace, hit
the ALB DNS name, then destroy. Costs money — run manually or nightly, never
in the default pytest suite.
"""
import subprocess
import json
import time

import httpx
import pytest


@pytest.mark.e2e
def test_e2e_alb_serves_traffic_after_apply(tmp_path):
    workspace_dir = tmp_path / "ecs-e2e"
    workspace_dir.mkdir()

    subprocess.run(["terraform", "init"], cwd=workspace_dir, check=True)
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=workspace_dir, check=True)

    try:
        outputs = json.loads(
            subprocess.run(
                ["terraform", "output", "-json"], cwd=workspace_dir, check=True, capture_output=True, text=True
            ).stdout
        )
        alb_dns = outputs["alb_dns_name"]["value"]

        # ECS deployment + health checks take a minute or two to stabilize
        for _ in range(20):
            try:
                response = httpx.get(f"http://{alb_dns}/health", timeout=5)
                if response.status_code == 200:
                    break
            except httpx.RequestError:
                pass
            time.sleep(15)
        else:
            pytest.fail("ALB never became healthy within the timeout")

        assert response.status_code == 200
    finally:
        subprocess.run(["terraform", "destroy", "-auto-approve"], cwd=workspace_dir, check=True)
```

## 6. `tests/README.md` — How to Run Each Layer

```markdown
# Tests

## Static checks (fast, no AWS calls)
    terraform fmt -check -recursive
    terraform validate
    tflint

## Policy scan
    checkov -d . --external-checks-dir tests/policy

## Script unit tests (mocked AWS via Stubber/moto)
    .venv/bin/python3 -m pytest tests/scripts/ -v -m "not smoke and not e2e"

## Smoke tests (real AWS, run after an apply)
    .venv/bin/python3 -m pytest tests/scripts/ -v -m smoke

## Integration / e2e tests (costs money, ephemeral apply+destroy)
    .venv/bin/python3 -m pytest tests/integration/ -v -m e2e
```
