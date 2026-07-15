"""Shared pytest fixtures for scripts/ unit tests."""
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
