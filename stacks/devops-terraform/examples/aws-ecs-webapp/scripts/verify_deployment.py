"""Post-apply verification CLI for the aws-ecs-webapp reference example.

Polls an ECS service until it reaches steady state (runningCount ==
desiredCount) or a timeout elapses. Intended to run after `terraform apply`
as the final step of a session's post-apply verification.
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Optional

import boto3
import click
from botocore.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def make_ecs_client(region: str) -> Any:
    """Create a boto3 ECS client with adaptive retries.

    Args:
        region: AWS region, e.g. "us-east-1".

    Returns:
        A configured boto3 ECS client.
    """
    config = Config(retries={"max_attempts": 5, "mode": "adaptive"})
    return boto3.client("ecs", region_name=region, config=config)


def get_service_status(
    cluster: str,
    service: str,
    region: str,
    client: Optional[Any] = None,
) -> dict[str, Any]:
    """Fetch the current status of an ECS service.

    Args:
        cluster: ECS cluster name.
        service: ECS service name.
        region: AWS region.
        client: Optional pre-built boto3 ECS client (for testing via Stubber).

    Returns:
        A dict with cluster, service, running_count, desired_count, and status.

    Raises:
        ValueError: If the service does not exist in the given cluster.
    """
    ecs = client or make_ecs_client(region)
    response = ecs.describe_services(cluster=cluster, services=[service])

    if not response["services"]:
        raise ValueError(f"service not found: {service} in cluster {cluster}")

    svc = response["services"][0]
    return {
        "cluster": cluster,
        "service": service,
        "running_count": svc["runningCount"],
        "desired_count": svc["desiredCount"],
        "status": svc["status"],
    }


def poll_service_steady_state(
    cluster: str,
    service: str,
    region: str,
    timeout_s: int = 300,
    poll_interval_s: int = 15,
    client: Optional[Any] = None,
) -> bool:
    """Poll until the ECS service reaches steady state or the timeout elapses.

    Args:
        cluster: ECS cluster name.
        service: ECS service name.
        region: AWS region.
        timeout_s: Maximum time to wait, in seconds.
        poll_interval_s: Time between polls, in seconds.
        client: Optional pre-built boto3 ECS client (for testing).

    Returns:
        True if the service reached steady state within the timeout, False otherwise.
    """
    run_id = str(uuid.uuid4())
    deadline = time.monotonic() + timeout_s

    logger.info(
        "Polling for steady state",
        extra={"run_id": run_id, "cluster": cluster, "service": service},
    )

    while time.monotonic() < deadline:
        status = get_service_status(cluster, service, region, client=client)
        if status["running_count"] == status["desired_count"] and status["status"] == "ACTIVE":
            logger.info(
                "Service reached steady state",
                extra={"run_id": run_id, "running_count": status["running_count"]},
            )
            return True

        logger.info(
            "Not yet steady, retrying",
            extra={
                "run_id": run_id,
                "running_count": status["running_count"],
                "desired_count": status["desired_count"],
            },
        )
        time.sleep(poll_interval_s)

    logger.error("Timed out waiting for steady state", extra={"run_id": run_id})
    return False


@click.command()
@click.option("--cluster", required=True, help="ECS cluster name")
@click.option("--service", required=True, help="ECS service name")
@click.option("--region", default="us-east-1", show_default=True, help="AWS region")
@click.option("--timeout", "timeout_s", default=300, show_default=True, help="Timeout in seconds")
def main(cluster: str, service: str, region: str, timeout_s: int) -> None:
    """Poll an ECS service until it reaches steady state, then exit 0/1."""
    steady = poll_service_steady_state(cluster, service, region, timeout_s=timeout_s)
    if not steady:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
