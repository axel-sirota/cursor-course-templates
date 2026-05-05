"""Tests for comment endpoints - MOCK PHASE."""

from fastapi.testclient import TestClient


def test_add_comment(client: TestClient, mock_auth_headers: dict[str, str]) -> None:
    """Test adding a comment to a post with auth."""
    response = client.post(
        "/api/posts/mock-post-123/comments",
        headers=mock_auth_headers,
        json={"content": "Great post!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Great post!"
    assert data["postId"] == "mock-post-123"


def test_list_comments(client: TestClient) -> None:
    """Test listing comments for a post (no auth required)."""
    response = client.get("/api/posts/mock-post-123/comments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_delete_comment(client: TestClient, mock_auth_headers: dict[str, str]) -> None:
    """Test deleting a comment with auth."""
    response = client.delete("/api/comments/mock-comment-789", headers=mock_auth_headers)
    assert response.status_code == 204


def test_add_comment_without_auth(client: TestClient) -> None:
    """Test adding a comment without auth fails."""
    response = client.post(
        "/api/posts/mock-post-123/comments",
        json={"content": "Great post!"},
    )
    assert response.status_code == 401
