"""
E2E API Tests
"""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_user_registration(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass123"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "userId" in data
    assert data["username"] == "testuser"


def test_user_login(client: TestClient):
    """Test user login."""
    # Register user first
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass123"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "userId" in data
    assert data["username"] == "testuser"


def test_create_post(client: TestClient):
    """Test creating a blog post."""
    # Register user
    user_response = client.post(
        "/api/auth/register",
        json={"username": "author", "password": "pass123"}
    )
    user_id = user_response.json()["userId"]
    
    # Create post
    response = client.post(
        "/api/posts",
        json={
            "title": "My First Post",
            "content": "This is the content of my first post.",
            "authorId": user_id
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "postId" in data
    assert data["title"] == "My First Post"
    assert data["content"] == "This is the content of my first post."
    assert data["authorId"] == user_id
    assert "createdAt" in data


def test_get_post(client: TestClient):
    """Test retrieving a blog post."""
    # Register user
    user_response = client.post(
        "/api/auth/register",
        json={"username": "author", "password": "pass123"}
    )
    user_id = user_response.json()["userId"]
    
    # Create post
    create_response = client.post(
        "/api/posts",
        json={
            "title": "Test Post",
            "content": "Test content",
            "authorId": user_id
        }
    )
    post_id = create_response.json()["postId"]
    
    # Get post
    response = client.get(f"/api/posts/{post_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["postId"] == post_id
    assert data["title"] == "Test Post"
    assert data["content"] == "Test content"


def test_create_comment(client: TestClient):
    """Test creating a comment on a post."""
    # Register user
    user_response = client.post(
        "/api/auth/register",
        json={"username": "author", "password": "pass123"}
    )
    user_id = user_response.json()["userId"]
    
    # Create post
    post_response = client.post(
        "/api/posts",
        json={
            "title": "Post with Comments",
            "content": "Content here",
            "authorId": user_id
        }
    )
    post_id = post_response.json()["postId"]
    
    # Create comment
    response = client.post(
        f"/api/posts/{post_id}/comments",
        json={
            "content": "Great post!",
            "authorId": user_id
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "commentId" in data
    assert data["postId"] == post_id
    assert data["content"] == "Great post!"
    assert data["authorId"] == user_id
    assert "createdAt" in data


def test_list_comments(client: TestClient):
    """Test listing comments for a post."""
    # Register user
    user_response = client.post(
        "/api/auth/register",
        json={"username": "author", "password": "pass123"}
    )
    user_id = user_response.json()["userId"]
    
    # Create post
    post_response = client.post(
        "/api/posts",
        json={
            "title": "Post with Multiple Comments",
            "content": "Content",
            "authorId": user_id
        }
    )
    post_id = post_response.json()["postId"]
    
    # Create multiple comments
    client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "First comment", "authorId": user_id}
    )
    client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "Second comment", "authorId": user_id}
    )
    
    # List comments
    response = client.get(f"/api/posts/{post_id}/comments")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "First comment"
    assert data[1]["content"] == "Second comment"

