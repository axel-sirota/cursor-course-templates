package com.example.blogapi.integration;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.blogapi.web.dto.AuthResponse;
import com.example.blogapi.web.dto.CommentResponse;
import com.example.blogapi.web.dto.CreateCommentRequest;
import com.example.blogapi.web.dto.CreatePostRequest;
import com.example.blogapi.web.dto.PostResponse;
import com.example.blogapi.web.dto.RegisterRequest;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

/**
 * Teaching-highlight test class: every test method documents its exact input and expected
 * output in the Javadoc/comments, mirroring the {@code test_scenarios.py} pattern from the
 * python-fastapi reference solution. Read this class top-to-bottom to see the full posts +
 * comments flow end to end against a real Postgres (Testcontainers).
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class PostAndCommentScenariosIntegrationTest extends AbstractIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    /**
     * Scenario: an authenticated user creates a post, then reads it back by id.
     *
     * <p>Input: {@code POST /api/auth/register} → {@code POST /api/posts} with a Bearer token →
     * {@code GET /api/posts/{id}} with no auth (public read).
     *
     * <p>Expected output: the post created in step 2 is retrievable, unauthenticated, in step 3,
     * with identical title/content and a real (non-mock) UUID and timestamp.
     */
    @Test
    void createPost_thenReadItBackPublicly() {
        String token = registerAndGetToken("post-author@example.com", "Post Author");

        CreatePostRequest createRequest = new CreatePostRequest("My First Post", "Hello, world!");
        HttpEntity<CreatePostRequest> authedRequest = new HttpEntity<>(createRequest, bearerHeaders(token));

        ResponseEntity<PostResponse> createResponse =
            restTemplate.postForEntity("/api/posts", authedRequest, PostResponse.class);

        assertThat(createResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        UUID postId = createResponse.getBody().postId();
        assertThat(postId).isNotNull();

        ResponseEntity<PostResponse> readResponse =
            restTemplate.getForEntity("/api/posts/{id}", PostResponse.class, postId);

        assertThat(readResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(readResponse.getBody().title()).isEqualTo("My First Post");
        assertThat(readResponse.getBody().content()).isEqualTo("Hello, world!");
    }

    /**
     * Scenario: creating a post without a Bearer token is rejected.
     *
     * <p>Input: {@code POST /api/posts} with no {@code Authorization} header.
     *
     * <p>Expected output: {@code 401 Unauthorized} — the Spring Security filter chain rejects
     * the request before it reaches {@code PostController}.
     */
    @Test
    void createPost_withoutToken_returns401() {
        CreatePostRequest createRequest = new CreatePostRequest("Unauthorized Post", "Should not be created");

        ResponseEntity<String> response = restTemplate.postForEntity("/api/posts", createRequest, String.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    /**
     * Scenario: fetching a post that doesn't exist returns a structured 404, not a raw stack
     * trace or an empty 200.
     *
     * <p>Input: {@code GET /api/posts/{random-uuid}} for a UUID that was never created.
     *
     * <p>Expected output: {@code 404 Not Found} with a {@code ProblemDetail} body whose {@code
     * detail} field names the missing post id.
     */
    @Test
    void getPost_nonexistentId_returns404WithProblemDetail() {
        UUID missingId = UUID.randomUUID();

        ResponseEntity<String> response = restTemplate.getForEntity("/api/posts/{id}", String.class, missingId);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        assertThat(response.getBody()).contains(missingId.toString());
    }

    /**
     * Scenario: a second authenticated user comments on the first user's post, and the comment
     * is visible via the public list-comments endpoint.
     *
     * <p>Input: user A registers and creates a post; user B registers and posts a comment on
     * user A's post; an unauthenticated client lists comments for that post.
     *
     * <p>Expected output: the comment list contains exactly one comment, authored by user B,
     * with the exact content submitted.
     */
    @Test
    void commentOnAnothersPost_thenListPublicly() {
        String authorToken = registerAndGetToken("post-owner@example.com", "Post Owner");
        CreatePostRequest createPost = new CreatePostRequest("A Post To Comment On", "Body text");
        ResponseEntity<PostResponse> postResponse = restTemplate.postForEntity(
            "/api/posts", new HttpEntity<>(createPost, bearerHeaders(authorToken)), PostResponse.class);
        UUID postId = postResponse.getBody().postId();

        String commenterToken = registerAndGetToken("commenter@example.com", "Commenter");
        CreateCommentRequest createComment = new CreateCommentRequest("Great writeup!");
        ResponseEntity<CommentResponse> commentResponse = restTemplate.postForEntity(
            "/api/posts/{postId}/comments",
            new HttpEntity<>(createComment, bearerHeaders(commenterToken)),
            CommentResponse.class,
            postId);

        assertThat(commentResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(commentResponse.getBody().content()).isEqualTo("Great writeup!");

        ResponseEntity<CommentResponse[]> listResponse = restTemplate.getForEntity(
            "/api/posts/{postId}/comments", CommentResponse[].class, postId);

        assertThat(listResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(listResponse.getBody()).hasSize(1);
        assertThat(listResponse.getBody()[0].content()).isEqualTo("Great writeup!");
    }

    /**
     * Scenario: commenting on a post that doesn't exist is rejected before any row is written.
     *
     * <p>Input: an authenticated user posts a comment to a random, never-created post id.
     *
     * <p>Expected output: {@code 404 Not Found} — {@code CommentService} checks {@code
     * postRepository.existsById()} before saving, so no orphaned comment row is created.
     */
    @Test
    void commentOnNonexistentPost_returns404() {
        String token = registerAndGetToken("orphan-commenter@example.com", "Orphan Commenter");
        UUID missingPostId = UUID.randomUUID();
        CreateCommentRequest createComment = new CreateCommentRequest("Comment on nothing");

        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/posts/{postId}/comments",
            new HttpEntity<>(createComment, bearerHeaders(token)),
            String.class,
            missingPostId);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    private String registerAndGetToken(String email, String fullName) {
        RegisterRequest registerRequest = new RegisterRequest(email, "supersecretpassword", fullName);
        ResponseEntity<AuthResponse> response =
            restTemplate.postForEntity("/api/auth/register", registerRequest, AuthResponse.class);
        return response.getBody().accessToken();
    }

    private HttpHeaders bearerHeaders(String token) {
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + token);
        return headers;
    }
}
