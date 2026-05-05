"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app.
    
    Returns:
        TestClient instance
    """
    return TestClient(app)


@pytest.fixture
def mock_auth_headers() -> dict[str, str]:
    """Create mock authentication headers.
    
    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": "Bearer mock-token"}
