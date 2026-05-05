"""Tests for post endpoints - MOCK PHASE."""

from fastapi.testclient import TestClient


def test_create_post(client: TestClient, mock_auth_headers: dict[str, str]) -> None:
    """Test creating a post with auth."""
    response = client.post(
        "/api/posts",
        headers=mock_auth_headers,
        json={
            "title": "Test Post",
            "content": "Test content",
            "tags": ["test"],
            "published": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "Test content"
    assert data["tags"] == ["test"]


def test_list_posts(client: TestClient) -> None:
    """Test listing posts (no auth required)."""
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "total" in data
    assert len(data["posts"]) == 3


def test_get_post(client: TestClient) -> None:
    """Test getting a single post by ID."""
    response = client.get("/api/posts/mock-post-123")
    assert response.status_code == 200
    data = response.json()
    assert data["postId"] == "mock-post-123"
    assert "title" in data
    assert "content" in data


def test_update_post(client: TestClient, mock_auth_headers: dict[str, str]) -> None:
    """Test updating a post with auth."""
    response = client.put(
        "/api/posts/mock-post-123",
        headers=mock_auth_headers,
        json={
            "title": "Updated Title",
            "content": "Updated content",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


def test_delete_post(client: TestClient, mock_auth_headers: dict[str, str]) -> None:
    """Test deleting a post with auth."""
    response = client.delete("/api/posts/mock-post-123", headers=mock_auth_headers)
    assert response.status_code == 204


def test_create_post_without_auth(client: TestClient) -> None:
    """Test creating a post without auth fails."""
    response = client.post(
        "/api/posts",
        json={
            "title": "Test Post",
            "content": "Test content",
        },
    )
    assert response.status_code == 401
