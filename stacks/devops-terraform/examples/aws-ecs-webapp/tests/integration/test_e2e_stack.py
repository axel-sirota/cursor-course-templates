"""e2e: apply the full aws-ecs-webapp stack into a throwaway state key, hit
the ALB DNS name, then destroy.

Costs money and takes several minutes to run (ECS steady state + ALB health
checks). Run manually or on a scheduled/nightly job — never in the default
pytest suite or PR pipeline. Requires real AWS credentials and a real ACM
certificate ARN / ECR image to be usable end to end.
"""
import json
import subprocess
import time

import httpx
import pytest


@pytest.mark.e2e
def test_e2e_alb_serves_traffic_after_apply(tmp_path):
    """Apply into a throwaway backend key, poll the ALB, then destroy."""
    project_root = tmp_path

    subprocess.run(
        [
            "terraform",
            "init",
            "-backend-config=bucket=acme-terraform-state",
            "-backend-config=key=aws-ecs-webapp/e2e-test/terraform.tfstate",
            "-backend-config=region=us-east-1",
            "-backend-config=use_lockfile=true",
        ],
        cwd=project_root,
        check=True,
    )
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=project_root, check=True)

    try:
        outputs = json.loads(
            subprocess.run(
                ["terraform", "output", "-json"],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        alb_dns = outputs["alb_dns_name"]["value"]

        response = None
        for _ in range(20):
            try:
                response = httpx.get(f"http://{alb_dns}/health", timeout=5, follow_redirects=True)
                if response.status_code == 200:
                    break
            except httpx.RequestError:
                pass
            time.sleep(15)
        else:
            pytest.fail("ALB never became healthy within the timeout")

        assert response is not None
        assert response.status_code == 200
    finally:
        # The one place `terraform destroy` is acceptable: a dedicated,
        # human-triggered, ephemeral e2e teardown — never real project state.
        subprocess.run(["terraform", "destroy", "-auto-approve"], cwd=project_root, check=True)
