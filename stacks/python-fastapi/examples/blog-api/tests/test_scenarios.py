"""
Test Scenarios with Expected Input/Output
Use these as examples when teaching students about E2E testing.
"""
import pytest
from fastapi.testclient import TestClient


class TestUserAuthenticationScenarios:
    """User authentication test scenarios."""
    
    def test_register_new_user_success(self, client: TestClient):
        """
        Scenario: Register a new user successfully
        
        Input:
            POST /api/auth/register
            {
                "username": "johndoe",
                "password": "secure123"
            }
        
        Expected Output:
            Status: 201
            {
                "userId": "<uuid>",
                "username": "johndoe"
            }
        """
        response = client.post(
            "/api/auth/register",
            json={"username": "johndoe", "password": "secure123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "userId" in data
        assert data["username"] == "johndoe"
        # UUID format validation
        assert len(data["userId"]) == 36  # UUID format
    
    def test_register_duplicate_username(self, client: TestClient):
        """
        Scenario: Try to register with existing username
        
        Input:
            First: POST /api/auth/register {"username": "johndoe", "password": "pass1"}
            Second: POST /api/auth/register {"username": "johndoe", "password": "pass2"}
        
        Expected Output:
            First: 201 success
            Second: 400 error with message about duplicate username
        """
        # First registration succeeds
        response1 = client.post(
            "/api/auth/register",
            json={"username": "johndoe", "password": "pass1"}
        )
        assert response1.status_code == 201
        
        # Second registration fails
        response2 = client.post(
            "/api/auth/register",
            json={"username": "johndoe", "password": "pass2"}
        )
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()
    
    def test_login_success(self, client: TestClient):
        """
        Scenario: Login with correct credentials
        
        Input:
            Setup: Register user with username="alice", password="wonderland"
            Then: POST /api/auth/login {"username": "alice", "password": "wonderland"}
        
        Expected Output:
            Status: 200
            {
                "userId": "<uuid>",
                "username": "alice"
            }
        """
        # Register user
        register_response = client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "wonderland"}
        )
        expected_user_id = register_response.json()["userId"]
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "wonderland"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == expected_user_id
        assert data["username"] == "alice"
    
    def test_login_wrong_password(self, client: TestClient):
        """
        Scenario: Login with wrong password
        
        Input:
            Setup: Register user with password="correct123"
            Then: POST /api/auth/login with password="wrong123"
        
        Expected Output:
            Status: 401
            {"detail": "Invalid credentials"}
        """
        # Register user
        client.post(
            "/api/auth/register",
            json={"username": "bob", "password": "correct123"}
        )
        
        # Login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"username": "bob", "password": "wrong123"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


class TestBlogPostScenarios:
    """Blog post test scenarios."""
    
    def test_create_post_success(self, client: TestClient):
        """
        Scenario: Create a blog post successfully
        
        Input:
            Setup: Register user and get userId
            POST /api/posts
            {
                "title": "My Travel Blog",
                "content": "I went to Paris and saw the Eiffel Tower!",
                "authorId": "<userId>"
            }
        
        Expected Output:
            Status: 201
            {
                "postId": "<uuid>",
                "title": "My Travel Blog",
                "content": "I went to Paris and saw the Eiffel Tower!",
                "authorId": "<userId>",
                "createdAt": "<ISO8601 timestamp>",
                "updatedAt": null or "<ISO8601 timestamp>"
            }
        """
        # Setup: Register user
        user_response = client.post(
            "/api/auth/register",
            json={"username": "traveler", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        # Create post
        response = client.post(
            "/api/posts",
            json={
                "title": "My Travel Blog",
                "content": "I went to Paris and saw the Eiffel Tower!",
                "authorId": user_id
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "postId" in data
        assert data["title"] == "My Travel Blog"
        assert data["content"] == "I went to Paris and saw the Eiffel Tower!"
        assert data["authorId"] == user_id
        assert "createdAt" in data
        # Verify ISO8601 format
        assert "T" in data["createdAt"]
    
    def test_create_post_empty_title(self, client: TestClient):
        """
        Scenario: Try to create post with empty title
        
        Input:
            POST /api/posts
            {
                "title": "",
                "content": "Some content",
                "authorId": "<userId>"
            }
        
        Expected Output:
            Status: 400
            {"detail": "Title cannot be empty"}
        """
        # Setup: Register user
        user_response = client.post(
            "/api/auth/register",
            json={"username": "writer", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        # Try to create post with empty title
        response = client.post(
            "/api/posts",
            json={
                "title": "",
                "content": "Some content",
                "authorId": user_id
            }
        )
        
        assert response.status_code == 400
        assert "title cannot be empty" in response.json()["detail"].lower()
    
    def test_create_post_title_too_long(self, client: TestClient):
        """
        Scenario: Try to create post with title > 200 characters
        
        Input:
            POST /api/posts with title of 201 characters
        
        Expected Output:
            Status: 400
            {"detail": "Title cannot exceed 200 characters"}
        """
        # Setup: Register user
        user_response = client.post(
            "/api/auth/register",
            json={"username": "writer2", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        # Create title that's too long
        long_title = "A" * 201
        
        response = client.post(
            "/api/posts",
            json={
                "title": long_title,
                "content": "Content",
                "authorId": user_id
            }
        )
        
        assert response.status_code == 400
        assert "200 characters" in response.json()["detail"]
    
    def test_get_post_success(self, client: TestClient):
        """
        Scenario: Get an existing post by ID
        
        Input:
            Setup: Create a post and get its postId
            GET /api/posts/{postId}
        
        Expected Output:
            Status: 200
            {
                "postId": "<uuid>",
                "title": "Test Post",
                "content": "Test content",
                "authorId": "<userId>",
                "createdAt": "<timestamp>",
                "updatedAt": null or "<timestamp>"
            }
        """
        # Setup: Register user and create post
        user_response = client.post(
            "/api/auth/register",
            json={"username": "reader", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        post_response = client.post(
            "/api/posts",
            json={
                "title": "Test Post",
                "content": "Test content",
                "authorId": user_id
            }
        )
        post_id = post_response.json()["postId"]
        
        # Get post
        response = client.get(f"/api/posts/{post_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["postId"] == post_id
        assert data["title"] == "Test Post"
        assert data["content"] == "Test content"
        assert data["authorId"] == user_id
    
    def test_get_nonexistent_post(self, client: TestClient):
        """
        Scenario: Try to get a post that doesn't exist
        
        Input:
            GET /api/posts/00000000-0000-0000-0000-000000000000
        
        Expected Output:
            Status: 404
            {"detail": "Post not found"}
        """
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/posts/{fake_uuid}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"


class TestCommentScenarios:
    """Comment test scenarios."""
    
    def test_create_comment_success(self, client: TestClient):
        """
        Scenario: Create a comment on a post
        
        Input:
            Setup: Create user and post
            POST /api/posts/{postId}/comments
            {
                "content": "Great article! Very informative.",
                "authorId": "<userId>"
            }
        
        Expected Output:
            Status: 201
            {
                "commentId": "<uuid>",
                "postId": "<uuid>",
                "content": "Great article! Very informative.",
                "authorId": "<userId>",
                "createdAt": "<timestamp>"
            }
        """
        # Setup: Register user and create post
        user_response = client.post(
            "/api/auth/register",
            json={"username": "commenter", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        post_response = client.post(
            "/api/posts",
            json={
                "title": "Article",
                "content": "Content",
                "authorId": user_id
            }
        )
        post_id = post_response.json()["postId"]
        
        # Create comment
        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={
                "content": "Great article! Very informative.",
                "authorId": user_id
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "commentId" in data
        assert data["postId"] == post_id
        assert data["content"] == "Great article! Very informative."
        assert data["authorId"] == user_id
        assert "createdAt" in data
    
    def test_create_comment_empty_content(self, client: TestClient):
        """
        Scenario: Try to create comment with empty content
        
        Input:
            POST /api/posts/{postId}/comments
            {
                "content": "",
                "authorId": "<userId>"
            }
        
        Expected Output:
            Status: 400
            {"detail": "Content cannot be empty"}
        """
        # Setup
        user_response = client.post(
            "/api/auth/register",
            json={"username": "user1", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        post_response = client.post(
            "/api/posts",
            json={"title": "Post", "content": "Content", "authorId": user_id}
        )
        post_id = post_response.json()["postId"]
        
        # Try to create comment with empty content
        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "", "authorId": user_id}
        )
        
        assert response.status_code == 400
        assert "content cannot be empty" in response.json()["detail"].lower()
    
    def test_create_comment_nonexistent_post(self, client: TestClient):
        """
        Scenario: Try to comment on post that doesn't exist
        
        Input:
            POST /api/posts/00000000-0000-0000-0000-000000000000/comments
            {
                "content": "Comment",
                "authorId": "<userId>"
            }
        
        Expected Output:
            Status: 400
            {"detail": "Post with ID ... not found"}
        """
        # Setup: Register user
        user_response = client.post(
            "/api/auth/register",
            json={"username": "user2", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        # Try to comment on nonexistent post
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/posts/{fake_uuid}/comments",
            json={"content": "Comment", "authorId": user_id}
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_comments_success(self, client: TestClient):
        """
        Scenario: List all comments for a post
        
        Input:
            Setup: Create post with 3 comments
            GET /api/posts/{postId}/comments
        
        Expected Output:
            Status: 200
            [
                {
                    "commentId": "<uuid1>",
                    "postId": "<postId>",
                    "content": "First comment",
                    "authorId": "<userId>",
                    "createdAt": "<timestamp1>"
                },
                {
                    "commentId": "<uuid2>",
                    "postId": "<postId>",
                    "content": "Second comment",
                    "authorId": "<userId>",
                    "createdAt": "<timestamp2>"
                },
                {
                    "commentId": "<uuid3>",
                    "postId": "<postId>",
                    "content": "Third comment",
                    "authorId": "<userId>",
                    "createdAt": "<timestamp3>"
                }
            ]
            
            Note: Comments should be ordered by createdAt ascending (oldest first)
        """
        # Setup: Register user and create post
        user_response = client.post(
            "/api/auth/register",
            json={"username": "blogger", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        post_response = client.post(
            "/api/posts",
            json={
                "title": "Popular Post",
                "content": "This got many comments",
                "authorId": user_id
            }
        )
        post_id = post_response.json()["postId"]
        
        # Create 3 comments
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "First comment", "authorId": user_id}
        )
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "Second comment", "authorId": user_id}
        )
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "Third comment", "authorId": user_id}
        )
        
        # List comments
        response = client.get(f"/api/posts/{post_id}/comments")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["content"] == "First comment"
        assert data[1]["content"] == "Second comment"
        assert data[2]["content"] == "Third comment"
        # Verify all have same postId
        assert all(comment["postId"] == post_id for comment in data)
    
    def test_list_comments_empty(self, client: TestClient):
        """
        Scenario: List comments for post with no comments
        
        Input:
            Setup: Create post with no comments
            GET /api/posts/{postId}/comments
        
        Expected Output:
            Status: 200
            []
        """
        # Setup: Register user and create post
        user_response = client.post(
            "/api/auth/register",
            json={"username": "lonely", "password": "pass123"}
        )
        user_id = user_response.json()["userId"]
        
        post_response = client.post(
            "/api/posts",
            json={
                "title": "No Comments Yet",
                "content": "Waiting for feedback",
                "authorId": user_id
            }
        )
        post_id = post_response.json()["postId"]
        
        # List comments (should be empty)
        response = client.get(f"/api/posts/{post_id}/comments")
        
        assert response.status_code == 200
        assert response.json() == []


class TestCompleteUserFlow:
    """Complete user flow scenarios."""
    
    def test_complete_blog_workflow(self, client: TestClient):
        """
        Scenario: Complete workflow from registration to commenting
        
        Flow:
            1. User registers
            2. User logs in
            3. User creates a blog post
            4. User retrieves the post
            5. User adds a comment
            6. User lists all comments
        
        This tests the entire application workflow.
        """
        # Step 1: Register
        register_response = client.post(
            "/api/auth/register",
            json={"username": "fulluser", "password": "secure123"}
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["userId"]
        
        # Step 2: Login
        login_response = client.post(
            "/api/auth/login",
            json={"username": "fulluser", "password": "secure123"}
        )
        assert login_response.status_code == 200
        assert login_response.json()["userId"] == user_id
        
        # Step 3: Create post
        post_response = client.post(
            "/api/posts",
            json={
                "title": "My First Blog Post",
                "content": "This is my journey into blogging!",
                "authorId": user_id
            }
        )
        assert post_response.status_code == 201
        post_id = post_response.json()["postId"]
        
        # Step 4: Retrieve post
        get_post_response = client.get(f"/api/posts/{post_id}")
        assert get_post_response.status_code == 200
        assert get_post_response.json()["title"] == "My First Blog Post"
        
        # Step 5: Add comment
        comment_response = client.post(
            f"/api/posts/{post_id}/comments",
            json={
                "content": "Great first post!",
                "authorId": user_id
            }
        )
        assert comment_response.status_code == 201
        
        # Step 6: List comments
        list_response = client.get(f"/api/posts/{post_id}/comments")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["content"] == "Great first post!"
    
    def test_multiple_users_interaction(self, client: TestClient):
        """
        Scenario: Multiple users interacting with same post
        
        Flow:
            1. User A creates post
            2. User B comments on it
            3. User C comments on it
            4. List all comments (should show both)
        """
        # User A registers and creates post
        user_a = client.post(
            "/api/auth/register",
            json={"username": "userA", "password": "pass123"}
        ).json()
        
        post = client.post(
            "/api/posts",
            json={
                "title": "Open for Discussion",
                "content": "What do you think?",
                "authorId": user_a["userId"]
            }
        ).json()
        
        # User B registers and comments
        user_b = client.post(
            "/api/auth/register",
            json={"username": "userB", "password": "pass123"}
        ).json()
        
        client.post(
            f"/api/posts/{post['postId']}/comments",
            json={
                "content": "User B's opinion here",
                "authorId": user_b["userId"]
            }
        )
        
        # User C registers and comments
        user_c = client.post(
            "/api/auth/register",
            json={"username": "userC", "password": "pass123"}
        ).json()
        
        client.post(
            f"/api/posts/{post['postId']}/comments",
            json={
                "content": "User C agrees!",
                "authorId": user_c["userId"]
            }
        )
        
        # List all comments
        comments_response = client.get(f"/api/posts/{post['postId']}/comments")
        comments = comments_response.json()
        
        assert len(comments) == 2
        assert comments[0]["authorId"] == user_b["userId"]
        assert comments[1]["authorId"] == user_c["userId"]

