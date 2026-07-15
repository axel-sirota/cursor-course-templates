# Test Documentation

## Overview
This folder contains comprehensive tests demonstrating the test-driven development approach
used in the session-based workflow, at every layer defined in `rules/400-testing-first.mdc`.

## Test Files

### `integration/AbstractIntegrationTest.java`
- Shared Testcontainers Postgres setup (one container per test class)
- Registers datasource properties dynamically via `@DynamicPropertySource`
- All integration test classes `extends AbstractIntegrationTest`

### `web/*ControllerTest.java`
- `@WebMvcTest` sliced controller tests — fast, no database, `@MockBean` services
- `AuthControllerTest`, `PostControllerTest`, `CommentControllerTest`
- Quick smoke tests for request/response mapping, validation, auth, status codes
- Use these for quick validation during active development

### `service/*ServiceTest.java`
- Mockito unit tests — fastest layer, no Spring context at all
- `PostServiceTest`, `CommentServiceTest`
- Exercise business-rule branches (title-too-short, post-must-exist-before-comment, etc.)

### `integration/PostAndCommentScenariosIntegrationTest.java` ⭐ **MAIN TEACHING REFERENCE**
- Complete test scenarios with detailed Javadoc documentation
- Each test includes:
  - **Scenario description**: what we're testing
  - **Input**: exact request sequence
  - **Expected output**: exact response format with status codes
- Runs against real Postgres via Testcontainers — no mocking of the datasource
- Covers the full posts + comments + auth flow end to end

### `integration/AuthIntegrationTest.java`
- Register → login round trip against real Postgres + real BCrypt hashing
- Duplicate email and wrong-password error cases

### `ApplicationTests.java`
- Smoke test: the full Spring context loads without errors against a real Postgres

## Running Tests

### Run all tests
```bash
cd examples/blog-api
./mvnw test
```

### Run only the fast layers (controller + unit, skip Testcontainers)
```bash
./mvnw test -Dtest='*ControllerTest,*ServiceTest'
```

### Run a specific test class
```bash
./mvnw test -Dtest=PostAndCommentScenariosIntegrationTest
```

### Run a specific test method
```bash
./mvnw test -Dtest=PostAndCommentScenariosIntegrationTest#createPost_thenReadItBackPublicly
```

### Run with coverage
```bash
./mvnw test jacoco:report
# report at target/site/jacoco/index.html
```

## Test Structure Best Practices

### 1. Arrange-Act-Assert Pattern
Every test follows this pattern:
```java
@Test
void createPost_success() {
    // Arrange: set up test data
    CreatePostRequest request = new CreatePostRequest("Title", "Body");

    // Act: perform the action
    ResponseEntity<PostResponse> response = restTemplate.postForEntity("/api/posts", ...);

    // Assert: verify the result
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
}
```

### 2. Clear Test Names
Test names describe the scenario:
- `createPost_successCase_returnsCreatedPost` — happy path
- `createPost_validationCase_blankTitleReturns400` — validation error
- `getPost_errorCase_returns404WhenMissing` — not found error

### 3. Documented Inputs/Outputs
Scenario tests document intent in Javadoc:
```java
/**
 * Scenario: what we're testing.
 *
 * <p>Input: exact request sequence.
 *
 * <p>Expected output: exact response format with status codes.
 */
@Test
void scenarioName() { ... }
```

### 4. Independent Tests
Each test:
- Registers its own users with unique emails
- Doesn't depend on other tests' data
- Can run in any order
- Testcontainers Postgres is shared per class but each test uses fresh, uniquely-emailed rows

## Teaching with These Tests

### Session 1: Show Students
1. **AbstractIntegrationTest** — how Testcontainers wiring works
2. **PostAndCommentScenariosIntegrationTest** — pick 2-3 examples:
   - `commentOnAnothersPost_thenListPublicly` (full flow, two users)
   - `createPost_withoutToken_returns401` (auth enforcement)
   - `getPost_nonexistentId_returns404WithProblemDetail` (structured errors)

### Key Points to Emphasize
- Tests document API behavior
- Input/output examples are the contract
- Tests fail first, then drive implementation (see `rules/400-testing-first.mdc`)
- Each test layer has a distinct purpose: unit (fast, isolated logic), controller (request
  mapping), integration (real database, real end-to-end flow)
- Descriptive names tell the story

### Student Exercise
Have students:
1. Read a scenario test
2. Understand the input/output format
3. Write a similar test for a new feature
4. Run the test and see it fail
5. Implement the feature to make it pass

## Test Coverage

### User Authentication
- Register new user
- Duplicate email handling
- Login success
- Login with wrong password

### Blog Posts
- Create post
- Blank title validation
- Get post by ID
- Get nonexistent post (404 with ProblemDetail)
- List posts, paginated

### Comments
- Create comment
- Blank content validation
- Comment on nonexistent post (404, no orphaned row)
- List comments

### Complete Flows
- Full two-user workflow (author creates post, second user comments, public read)

## Common Test Patterns

### Pattern 1: Simple Success Case
```java
@Test
void action_success() {
    ResponseEntity<X> response = restTemplate.postForEntity("/endpoint", request, X.class);
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    assertThat(response.getBody().id()).isNotNull();
}
```

### Pattern 2: Validation Error
```java
@Test
void action_validationError() {
    ResponseEntity<String> response = restTemplate.postForEntity("/endpoint", invalidRequest, String.class);
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
}
```

### Pattern 3: Not Found
```java
@Test
void getNonexistent_returns404() {
    ResponseEntity<String> response = restTemplate.getForEntity("/endpoint/{id}", String.class, fakeId);
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
}
```

### Pattern 4: With Setup
```java
@Test
void actionWithSetup() {
    String token = registerAndGetToken("user@example.com", "User");
    ResponseEntity<PostResponse> post = restTemplate.postForEntity(
        "/api/posts", new HttpEntity<>(createRequest, bearerHeaders(token)), PostResponse.class);

    ResponseEntity<CommentResponse> comment = restTemplate.postForEntity(
        "/api/posts/{id}/comments", new HttpEntity<>(commentRequest, bearerHeaders(token)),
        CommentResponse.class, post.getBody().postId());

    assertThat(comment.getStatusCode()).isEqualTo(HttpStatus.OK);
}
```

## Debugging Failed Tests

### View detailed output
```bash
./mvnw test -Dtest=PostAndCommentScenariosIntegrationTest -Dsurefire.printSummary=true
```

### Enable SQL logging
Set `SQL_LOG_LEVEL=DEBUG` (see `application-dev.yml`) or run with the `dev` profile active.

### Check database state
Testcontainers Postgres is ephemeral and destroyed after the test class finishes. To inspect it
mid-run, add a breakpoint in a test method and connect with `psql` using the JDBC URL logged by
Testcontainers at container startup.

## Next Steps
After understanding these tests:
1. Use them as templates for new features
2. Adapt patterns to your specific needs
3. Keep documentation (Javadoc) updated
4. Add edge cases as you find them
