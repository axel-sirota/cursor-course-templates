"""Tests for tag endpoints - MOCK PHASE."""

from fastapi.testclient import TestClient


def test_list_tags(client: TestClient) -> None:
    """Test listing all tags."""
    response = client.get("/api/tags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["name"] == "python"
    assert "postCount" in data[0]


def test_get_posts_by_tag(client: TestClient) -> None:
    """Test getting posts filtered by tag."""
    response = client.get("/api/tags/python/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["tag"] == "python"
    assert "posts" in data
    assert len(data["posts"]) == 2
    assert data["total"] == 2
