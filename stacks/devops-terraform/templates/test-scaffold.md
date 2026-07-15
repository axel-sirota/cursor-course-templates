# Test Scaffold: pytest + moto + checkov + integration

Copy the relevant sections below into `tests/` when starting a new module's validation-first check.

## 1. `tests/scripts/conftest.py` — Shared Fixtures

```python
"""Shared pytest fixtures for automation-script unit tests."""
import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws_credentials(monkeypatch):
    """Mocked AWS credentials so boto3 never touches real credentials."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def ecs_client(aws_credentials):
    """A moto-mocked ECS client."""
    with mock_aws():
        yield boto3.client("ecs", region_name="us-east-1")


@pytest.fixture
def ecs_cluster(ecs_client):
    """A cluster pre-created in the moto-mocked ECS backend."""
    ecs_client.create_cluster(clusterName="acme-test-cluster")
    return "acme-test-cluster"
```

## 2. `tests/scripts/test_verify_deployment.py` — moto Unit Test Pattern

```python
"""Unit tests for scripts/verify_deployment.py, mocked via moto."""
import pytest

from scripts.verify_deployment import get_service_status


def test_HP_verify_deployment_reports_steady_state(ecs_client, ecs_cluster):
    """HP: a healthy service reports runningCount == desiredCount."""
    # moto's ECS service support is partial — for deep service-state
    # coverage prefer botocore.stub.Stubber (see below) over moto here.
    ...


def test_UP_verify_deployment_missing_service_raises(ecs_client, ecs_cluster):
    """UP: an unknown service name raises a clear, typed error."""
    with pytest.raises(ValueError, match="service not found"):
        get_service_status(
            cluster=ecs_cluster,
            service="does-not-exist",
            region="us-east-1",
            client=ecs_client,
        )
```

## 3. `tests/scripts/test_verify_deployment_stubber.py` — Stubber Pattern (Deep Response Control)

```python
"""Stubber gives exact control over the AWS response shape moto can't fully model."""
import boto3
from botocore.stub import Stubber

from scripts.verify_deployment import get_service_status


def test_HP_get_service_status_steady_state():
    client = boto3.client("ecs", region_name="us-east-1")
    stubber = Stubber(client)
    stubber.add_response(
        "describe_services",
        {
            "services": [
                {
                    "serviceName": "acme-dev-web",
                    "runningCount": 2,
                    "desiredCount": 2,
                    "status": "ACTIVE",
                }
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
    stubber.deactivate()
```

## 4. `tests/policy/check_alb_https_only.py` — checkov Custom Check

```python
"""Custom checkov check: ALB HTTP listeners must redirect to HTTPS."""
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ALBHttpsOnly(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Ensure ALB listener on port 80 redirects to HTTPS",
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


check = ALBHttpsOnly()
```

## 5. `.checkov.yaml` — Skip-With-Justification Pattern

```yaml
# .checkov.yaml
directory:
  - .
external-checks-dir:
  - tests/policy
skip-check:
  - id: CKV_AWS_130
    # Justification: dev-environment public subnets intentionally assign
    # public IPs for course demo reachability. Production module sets
    # map_public_ip_on_launch = false. See plan/architecture/resources.md.
compact: true
quiet: true
```

## 6. `tests/integration/test_vpc_module_e2e.py` — Ephemeral-Apply Integration Test

```python
"""e2e: apply modules/vpc into a throwaway workspace, assert, then destroy.

Costs money and takes minutes to run — mark it explicitly and exclude it
from the default pytest run (see pytest.ini marker config below).
"""
import json
import subprocess

import pytest


@pytest.mark.e2e
def test_e2e_vpc_module_creates_expected_subnet_count(tmp_path):
    workspace_dir = tmp_path / "vpc-e2e"
    workspace_dir.mkdir()

    subprocess.run(["terraform", "init"], cwd=workspace_dir, check=True)
    subprocess.run(
        ["terraform", "apply", "-auto-approve", "-var", "availability_zone_count=2"],
        cwd=workspace_dir,
        check=True,
    )
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=workspace_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        outputs = json.loads(result.stdout)
        assert len(outputs["private_subnet_ids"]["value"]) == 2
    finally:
        # The one place `terraform destroy` is acceptable: a dedicated,
        # human-triggered, ephemeral-workspace teardown — never real state.
        subprocess.run(["terraform", "destroy", "-auto-approve"], cwd=workspace_dir, check=True)
```

## 7. `pytest.ini` — Marker Registration

```ini
[pytest]
markers =
    unit: fast, no AWS calls
    hp: happy-path integration, mocked AWS
    up: unhappy-path integration, mocked AWS
    e2e: real terraform apply/destroy, costs money, run manually or nightly
addopts = -m "not e2e"
```

## 8. `scripts/requirements.txt` — Testing Dependencies

```
pytest==8.3.0
moto[ec2,ecs,s3,elbv2]==5.0.13
boto3==1.35.0
botocore==1.35.0
```
