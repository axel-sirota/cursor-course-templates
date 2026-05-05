"""Tests for authentication endpoints - MOCK PHASE."""

from fastapi.testclient import TestClient


def test_register_user(client: TestClient) -> None:
    """Test user registration returns mock token."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["accessToken"].startswith("mock-jwt-token-")
    assert data["tokenType"] == "bearer"


def test_login_user(client: TestClient) -> None:
    """Test user login returns mock token."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"


def test_get_current_user_with_auth(
    client: TestClient,
    mock_auth_headers: dict[str, str],
) -> None:
    """Test getting current user profile with auth."""
    response = client.get("/api/auth/me", headers=mock_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "mockuser"
    assert data["email"] == "mockuser@example.com"


def test_get_current_user_without_auth(client: TestClient) -> None:
    """Test getting current user profile without auth fails."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
