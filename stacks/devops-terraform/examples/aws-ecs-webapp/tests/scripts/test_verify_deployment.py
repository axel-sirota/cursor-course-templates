"""Unit tests for scripts/verify_deployment.py.

Uses botocore.stub.Stubber for exact response control (moto's ECS service
support doesn't model runningCount/desiredCount deeply enough for these
scenarios), never calling real AWS.
"""
import boto3
import pytest
from botocore.stub import Stubber

from scripts.verify_deployment import get_service_status, poll_service_steady_state


def test_HP_get_service_status_steady_state():
    """HP: a healthy service reports runningCount == desiredCount == status ACTIVE."""
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

    assert status["running_count"] == status["desired_count"] == 2
    assert status["status"] == "ACTIVE"
    stubber.deactivate()


def test_HP_poll_service_steady_state_returns_true_immediately():
    """HP: polling returns True on the first check when already steady."""
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

    result = poll_service_steady_state(
        cluster="acme-dev-cluster",
        service="acme-dev-web",
        region="us-east-1",
        timeout_s=60,
        client=client,
    )

    assert result is True
    stubber.deactivate()


def test_UP_get_service_status_missing_service_raises():
    """UP: an unknown service name raises a clear ValueError, not a raw KeyError."""
    client = boto3.client("ecs", region_name="us-east-1")
    stubber = Stubber(client)
    stubber.add_response(
        "describe_services",
        {"services": [], "failures": [{"arn": "arn:aws:ecs:us-east-1:123:service/does-not-exist", "reason": "MISSING"}]},
        {"cluster": "acme-dev-cluster", "services": ["does-not-exist"]},
    )
    stubber.activate()

    with pytest.raises(ValueError, match="service not found"):
        get_service_status(
            cluster="acme-dev-cluster", service="does-not-exist", region="us-east-1", client=client
        )

    stubber.deactivate()


def test_UP_poll_service_steady_state_times_out(monkeypatch):
    """UP: polling returns False when the service never reaches steady state before timeout."""
    client = boto3.client("ecs", region_name="us-east-1")
    stubber = Stubber(client)

    # Two polls, both under-provisioned; monkeypatch time.sleep to avoid a
    # real wait, and force the monotonic clock to expire after 2 iterations.
    for _ in range(2):
        stubber.add_response(
            "describe_services",
            {
                "services": [
                    {"serviceName": "acme-dev-web", "runningCount": 1, "desiredCount": 2, "status": "ACTIVE"}
                ],
                "failures": [],
            },
            {"cluster": "acme-dev-cluster", "services": ["acme-dev-web"]},
        )
    stubber.activate()

    monkeypatch.setattr("scripts.verify_deployment.time.sleep", lambda _: None)

    result = poll_service_steady_state(
        cluster="acme-dev-cluster",
        service="acme-dev-web",
        region="us-east-1",
        timeout_s=0,  # deadline already passed on first check
        client=client,
    )

    assert result is False
    stubber.deactivate()
